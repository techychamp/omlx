# SPDX-License-Identifier: Apache-2.0
"""
Tests for Compiler-Native Diffusion Execution Integration.
"""

import pytest
from unittest.mock import MagicMock
import uuid

from omlx.runtime.execution.engine import ExecutionEngine
from omlx.runtime.execution.context import ExecutionContext
from omlx.runtime.execution.artifacts import BackendOperationGraph
from omlx.runtime.session import RuntimeSession
from omlx.planner.domains.diffusion.transformation.artifacts import (
    DiffusionExecutionGraph, LatentExecutionGraph, ConditioningExecutionGraph, RealizedTimestepGraph
)
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.runtime.observability import Observer, get_observer, set_observer, reset_observer
from omlx.runtime.generation.diffusion import DiffusionGenerationStrategy
from omlx.planner.domains.diffusion import DiffusionPlan

@pytest.fixture(autouse=True)
def observer_setup():
    observer = Observer(run_id="test_diffusion_execution")
    set_observer(observer)
    yield observer
    reset_observer()

def test_diffusion_execution_engine(observer_setup):
    # Mock Executor
    mock_executor = MagicMock()
    from omlx.runtime.execution.types import ExecutionResult, ExecutionStatus
    mock_executor.execute.return_value = ExecutionResult(status=ExecutionStatus.COMPLETED, model_output=None, execution_duration_ms=150.0)

    engine = ExecutionEngine(executor=mock_executor)

    # Construct Mock DiffusionExecutionGraph
    latent_graph = LatentExecutionGraph(nodes=(IRNode("l1", IRNodeType.FORWARD, ()),))
    conditioning_graph = ConditioningExecutionGraph(nodes=(IRNode("c1", IRNodeType.FORWARD, ()),))
    timesteps = (
        RealizedTimestepGraph(timestep=1, nodes=()),
        RealizedTimestepGraph(timestep=2, nodes=()),
        RealizedTimestepGraph(timestep=3, nodes=())
    )
    diffusion_graph = DiffusionExecutionGraph(
        latent_graph=latent_graph,
        conditioning_graph=conditioning_graph,
        timesteps=timesteps
    )

    context = ExecutionContext(
        backend_operation_graph=MagicMock(),
        diffusion_execution_graph=diffusion_graph
    )

    session = RuntimeSession(
        session_id=str(uuid.uuid4()),
        execution_context=context
    )

    result = engine.execute(session)

    # Assert executor was called 5 times (latent, conditioning, and 3 timesteps)
    assert mock_executor.execute.call_count == 5

    # Assert Report was emitted
    report = get_observer().artifact_tracker.get("DiffusionExecutionReport")
    assert report is not None
    assert report.total_timesteps_executed == 3
    assert report.execution_latency_ms == 750.0


def test_diffusion_generation_strategy(observer_setup):
    # Track a mock transformation report
    mock_diffusion_graph = DiffusionExecutionGraph(
        latent_graph=LatentExecutionGraph(nodes=()),
        conditioning_graph=ConditioningExecutionGraph(nodes=()),
        timesteps=(RealizedTimestepGraph(1, ()),)
    )

    # Setup mocks
    mock_runtime = MagicMock()
    mock_runtime.compiler_service.run_compilation.return_value = MagicMock(
        backend_graph=MagicMock(),
        diffusion_execution_graph=mock_diffusion_graph
    )
    mock_runtime.adapter_registry.resolve.return_value = MagicMock()
    mock_result = MagicMock()
    mock_result.model_output = "mock_output"
    mock_runtime.execution_engine.execute.return_value = mock_result    # Track a mock execution report (since we mocked engine.execute)
    from omlx.runtime.execution.diagnostics import DiffusionExecutionReport
    mock_execution_report = DiffusionExecutionReport(total_timesteps_executed=1, execution_latency_ms=10.0)
    observer_setup.artifact_tracker.track("DiffusionExecutionReport", mock_execution_report)

    mock_plan = DiffusionPlan(
        descriptor=MagicMock(),
        requirement=MagicMock(),
        timestep_schedule=[1],
        denoising_plan={"type": "standard"},
        validation=MagicMock()
    )

    strategy = DiffusionGenerationStrategy(plan=mock_plan)

    request_context = MagicMock(model="test_model")

    result = strategy.generate(runtime=mock_runtime, request_context=request_context)

    # Verification
    assert result["status"] == "success"
    assert result["diffusion_report"] == mock_execution_report
    assert result["model_output"] == "mock_output"

    # Ensure RuntimeSession was created and engine was called
    mock_runtime.execution_engine.execute.assert_called_once()
    called_session = mock_runtime.execution_engine.execute.call_args[0][0]
    assert isinstance(called_session, RuntimeSession)
    assert called_session.execution_context.diffusion_execution_graph == mock_diffusion_graph
    assert called_session.execution_context.adapter == mock_runtime.adapter_registry.resolve.return_value
