import pytest
from types import MappingProxyType
import time
from omlx.planner.domains.speculation.artifacts import (
    SpeculativeExecutionGraph,
    DraftExecutionGraph,
    VerificationExecutionGraph,
    AcceptanceExecutionGraph,
    SpeculativeExecutionDescriptor
)
from omlx.framework.graph.descriptor import GraphDescriptor
from omlx.runtime.execution.engine import ExecutionEngine
from omlx.runtime.execution.context import ExecutionContext
from omlx.runtime.session import RuntimeSession
from omlx.runtime.execution.artifacts import (
    SpeculativeExecutionReport,
    VerificationExecutionReport,
    AcceptanceExecutionReport,
    RollbackExecutionReport
)
from omlx.runtime.execution.types import ExecutionResult, ExecutionStatus
from omlx.runtime.execution.interfaces import ExecutionExecutor

class MockExecutor(ExecutionExecutor):
    def __init__(self, verification_outcome=True):
        self.verification_outcome = verification_outcome
        self.executed_graphs = []

    def execute(self, graph, context):
        from omlx.runtime.execution.artifacts import VerificationResult
        self.executed_graphs.append(graph.id)
        if "verify" in graph.id:
            return ExecutionResult(status=ExecutionStatus.COMPLETED, model_output=VerificationResult(accepted=self.verification_outcome))
        return ExecutionResult(status=ExecutionStatus.COMPLETED, model_output={})

def create_mock_speculative_graph():
    desc = SpeculativeExecutionDescriptor(
        draft_model_id="draft",
        target_model_id="target",
        draft_length=3
    )
    draft = DraftExecutionGraph(
        id="draft_exec",
        graph=GraphDescriptor(id="draft_graph", nodes=MappingProxyType({}), edges=tuple())
    )
    verify = VerificationExecutionGraph(
        id="verify_exec",
        graph=GraphDescriptor(id="verify_graph", nodes=MappingProxyType({}), edges=tuple())
    )
    accept = AcceptanceExecutionGraph(
        id="accept_exec",
        graph=GraphDescriptor(id="accept_graph", nodes=MappingProxyType({}), edges=tuple())
    )
    return SpeculativeExecutionGraph(
        id="spec_graph",
        draft_graph=draft,
        verification_graph=verify,
        acceptance_graph=accept,
        descriptor=desc
    )

def test_speculative_execution_accepted():
    session = RuntimeSession.create()
    spec_graph = create_mock_speculative_graph()
    session.execution_context = ExecutionContext(
        speculative_execution_graph=spec_graph
    )

    executor = MockExecutor(verification_outcome=True)
    engine = ExecutionEngine(executor=executor)

    result = engine.execute(session)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["accepted"] is True
    assert "draft_graph" in executor.executed_graphs
    assert "verify_graph" in executor.executed_graphs
    assert "accept_graph" in executor.executed_graphs

    assert session.draft_tokens == (1, 2, 3)
    assert session.accepted_tokens == (1, 2, 3)
    assert session.rejected_tokens == tuple()

    reports = session.speculative_reports
    assert any(isinstance(r, VerificationExecutionReport) for r in reports)
    assert any(isinstance(r, AcceptanceExecutionReport) for r in reports)
    assert any(isinstance(r, SpeculativeExecutionReport) for r in reports)
    assert not any(isinstance(r, RollbackExecutionReport) for r in reports)

def test_speculative_execution_rejected():
    session = RuntimeSession.create()
    spec_graph = create_mock_speculative_graph()
    session.execution_context = ExecutionContext(
        speculative_execution_graph=spec_graph
    )

    executor = MockExecutor(verification_outcome=False)
    engine = ExecutionEngine(executor=executor)

    result = engine.execute(session)

    assert result.status == ExecutionStatus.COMPLETED
    assert result.model_output["accepted"] is False
    assert "draft_graph" in executor.executed_graphs
    assert "verify_graph" in executor.executed_graphs
    assert "accept_graph" not in executor.executed_graphs  # Shouldn't execute on reject

    assert session.draft_tokens == (1, 2, 3)
    assert session.accepted_tokens == tuple()
    assert session.rejected_tokens == (1, 2, 3)

    reports = session.speculative_reports
    assert any(isinstance(r, VerificationExecutionReport) for r in reports)
    assert not any(isinstance(r, AcceptanceExecutionReport) for r in reports)
    assert any(isinstance(r, RollbackExecutionReport) for r in reports)
    assert any(isinstance(r, SpeculativeExecutionReport) for r in reports)

def test_speculative_execution_cache_consistency():
    """Verify that speculative execution does not break cache session semantics."""
    session = RuntimeSession.create()

    class MockCacheSession:
        def __init__(self):
            # A simple stub simulating the presence of a CACHE-002 cache session
            from types import SimpleNamespace
            self.cache_plan = SimpleNamespace(plan_id="test_cache_plan")
            self.state = "active"

    session.cache_session = MockCacheSession()

    spec_graph = create_mock_speculative_graph()
    session.execution_context = ExecutionContext(
        speculative_execution_graph=spec_graph,
        cache_session=session.cache_session
    )

    executor = MockExecutor(verification_outcome=True)
    engine = ExecutionEngine(executor=executor)

    result = engine.execute(session)

    # Must complete execution successfully without throwing or mutating cache inappropriately
    assert result.status == ExecutionStatus.COMPLETED
    assert session.cache_session.state == "active"
    assert getattr(session.execution_context, "cache_session") is not None
