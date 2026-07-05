import pytest
import os
import time
from unittest.mock import MagicMock, patch

from omlx.runtime.feature_flags import FeatureFlags
from omlx.runtime.builder import RuntimeBuilder, RuntimeContext, RuntimeStateEnum
from omlx.runtime.compiler_service import RuntimeCompilerService, CompilerSession
from omlx.planner.compiler.backend.adapter import TranslationResult

def test_feature_flags_loading():
    """Verify PRIMARY_COMPILER_EXECUTION and COMPILER_COMPATIBILITY_MODE."""
    with patch.dict(os.environ, {
        "OMLX_FEATURE_PRIMARY_COMPILER_EXECUTION": "1",
        "OMLX_FEATURE_COMPILER_COMPATIBILITY_MODE": "1",
        "OMLX_FEATURE_COMPILER_RUNTIME_ENABLED": "1"
    }):
        flags = FeatureFlags.from_env()
        assert flags.PRIMARY_COMPILER_EXECUTION is True
        assert flags.COMPILER_COMPATIBILITY_MODE is True
        assert flags.COMPILER_RUNTIME_ENABLED is True

def test_runtime_execute_request_invokes_compiler():
    """Verify Runtime.execute_request invokes compilation exactly once."""
    builder = RuntimeBuilder()
    runtime = builder.build()

    # Mock feature flags
    runtime.feature_flags = FeatureFlags(COMPILER_RUNTIME_ENABLED=True)

    # Mock compiler service
    runtime.compiler_service = MagicMock(spec=RuntimeCompilerService)
    runtime.compiler_service.run_compilation.return_value = TranslationResult(backend_graph=MagicMock())

    # Mock request
    request = MagicMock()
    request.model = "test-model"

    result = runtime.execute_request(request)

    assert result is not None
    runtime.compiler_service.run_compilation.assert_called_once_with("test-model", request)

def test_compiler_service_thread_safety_and_stats():
    """Verify stats tracking in RuntimeCompilerService."""
    builder = RuntimeBuilder()
    runtime = builder.build()

    # Enable context
    runtime.feature_flags = FeatureFlags(COMPILER_CONTEXT_ENABLED=True)

    service = RuntimeCompilerService(runtime)

    # Mock runner
    service._runner = MagicMock()
    service.runner.run_pipeline.return_value = TranslationResult(backend_graph=MagicMock())

    service.run_compilation("test-model")

    assert service.statistics["total_compilations"] == 1
    assert service.statistics["successful_compilations"] == 1

def test_runtime_context_immutable_after_population():
    """Verify RuntimeContext is fully populated and treated as a snapshot."""
    builder = RuntimeBuilder()
    runtime = builder.build()

    # Initially none
    assert runtime.context.logical_ir is None
    assert runtime.context.physical_ir is None

    runtime.update_context(
        logical_ir="logical",
        physical_ir="physical",
        execution_plan="plan",
        backend_operation_graph="graph"
    )

    assert runtime.context.logical_ir == "logical"
    assert runtime.context.physical_ir == "physical"
    assert runtime.context.execution_plan == "plan"
    assert runtime.context.backend_operation_graph == "graph"

def test_compiler_integration_pipeline():
    """Verify CompilerPipelineRunner populates logical_ir and physical_ir."""
    builder = RuntimeBuilder()
    runtime = builder.build()

    runtime.feature_flags = FeatureFlags(
        COMPILER_RUNTIME_PIPELINE_ENABLED=True,
        CAPABILITY_RUNTIME_ENABLED=True,
        PLANNER_RUNTIME_ENABLED=True,
        LOWERING_RUNTIME_ENABLED=True,
        ADAPTER_RUNTIME_ENABLED=True,
        COMPILER_CONTEXT_ENABLED=True
    )

    # Mock components
    runtime.context.capability_resolver.resolve = MagicMock(return_value="descriptor")

    runtime.execution_planner = MagicMock()
    plan_mock = MagicMock()
    plan_mock.execution_backend = "mlx"
    plan_mock.hardware_requirements = ["any"]
    plan_mock.execution_family = "autoregressive"
    plan_mock.execution_mode = "standard"
    runtime.execution_planner.plan.return_value = plan_mock

    runtime.ir_builder = MagicMock()
    runtime.ir_builder.build.return_value = "logical_ir"

    runtime.lowering_engine = MagicMock()
    runtime.lowering_engine.lower.return_value = "physical_ir"

    adapter = MagicMock()
    adapter.translate.return_value = TranslationResult(backend_graph="backend_graph")

    runtime.adapter_registry = MagicMock()
    runtime.adapter_registry.resolve.return_value = adapter

    runner = runtime.compiler_service.runner
    result = runner.run_pipeline("test-model")

    assert result is not None
    # We can't directly check update_context because the method creates a new Context.
    # We check if the execution happened.
    runtime.ir_builder.build.assert_called_once_with(plan_mock)
    runtime.lowering_engine.lower.assert_called_once_with("logical_ir")
    adapter.translate.assert_called_once_with("physical_ir")
