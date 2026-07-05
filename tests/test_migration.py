import pytest
from unittest.mock import MagicMock
from omlx.runtime.compiler_integration import CompilerPipelineRunner
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.compiler.backend.adapter import TranslationResult

@pytest.fixture
def mock_runtime():
    runtime = MagicMock()
    runtime.feature_flags = MagicMock()
    runtime.feature_flags.COMPILER_RUNTIME_PIPELINE_ENABLED = True
    runtime.feature_flags.CAPABILITY_RUNTIME_ENABLED = True
    runtime.feature_flags.PLANNER_RUNTIME_ENABLED = True
    runtime.feature_flags.LOWERING_RUNTIME_ENABLED = True
    runtime.feature_flags.ADAPTER_RUNTIME_ENABLED = True

    runtime.context = MagicMock()
    runtime.context.capability_resolver = MagicMock()
    runtime.context.capability_resolver.resolve.return_value = "mock_descriptor"

    runtime.execution_planner = MagicMock()
    mock_plan = MagicMock()
    mock_plan.execution_backend = "mlx"
    mock_plan.execution_family = "autoregressive"
    mock_plan.execution_mode = "standard"
    mock_plan.hardware_requirements = ("any",)
    runtime.execution_planner.plan.return_value = mock_plan

    runtime.ir_builder = MagicMock()
    runtime.ir_builder.build.return_value = MagicMock()

    runtime.lowering_engine = MagicMock()
    runtime.lowering_engine.lower.return_value = MagicMock()

    runtime.adapter_registry = MagicMock()
    mock_adapter = MagicMock()
    mock_translation_result = MagicMock(spec=TranslationResult)
    mock_adapter.translate.return_value = mock_translation_result
    runtime.adapter_registry.get_adapter.return_value = mock_adapter

    return runtime

def test_compiler_pipeline_runner_full(mock_runtime):
    runner = CompilerPipelineRunner(mock_runtime)
    result = runner.run_pipeline("test_model")

    assert result is not None
    mock_runtime.context.capability_resolver.resolve.assert_called_once()
    mock_runtime.execution_planner.plan.assert_called_once_with("mock_descriptor")
    mock_runtime.ir_builder.build.assert_called_once()
    mock_runtime.lowering_engine.lower.assert_called_once()
    mock_runtime.adapter_registry.get_adapter.assert_called_once()

def test_compiler_pipeline_runner_disabled(mock_runtime):
    mock_runtime.feature_flags.COMPILER_RUNTIME_PIPELINE_ENABLED = False
    runner = CompilerPipelineRunner(mock_runtime)
    result = runner.run_pipeline("test_model")

    assert result is None
    mock_runtime.context.capability_resolver.resolve.assert_not_called()

def test_compiler_pipeline_runner_partial(mock_runtime):
    mock_runtime.feature_flags.LOWERING_RUNTIME_ENABLED = False
    runner = CompilerPipelineRunner(mock_runtime)
    result = runner.run_pipeline("test_model")

    assert result is None
    mock_runtime.context.capability_resolver.resolve.assert_called_once()
    mock_runtime.execution_planner.plan.assert_called_once()
    mock_runtime.ir_builder.build.assert_not_called()
    mock_runtime.lowering_engine.lower.assert_not_called()
    mock_runtime.adapter_registry.get_adapter.assert_not_called()
