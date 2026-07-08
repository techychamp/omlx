import pytest
from omlx.planner.domains.speculation.artifacts import (
    SpeculativeExecutionDescriptor,
    SpeculativeExecutionGraph,
    DraftExecutionGraph,
    VerificationExecutionGraph,
    AcceptanceExecutionGraph,
)
from omlx.planner.domains.speculation.realizer import SpeculativeRealizer

def test_speculative_realizer_basic():
    descriptor = SpeculativeExecutionDescriptor(
        draft_model_id="tiny_model",
        target_model_id="large_model",
        draft_length=4
    )

    realizer = SpeculativeRealizer()
    report = realizer.realize(descriptor)

    assert report.success is True
    assert report.speculative_graph is not None
    assert isinstance(report.speculative_graph, SpeculativeExecutionGraph)

    graph = report.speculative_graph
    assert isinstance(graph.draft_graph, DraftExecutionGraph)
    assert isinstance(graph.verification_graph, VerificationExecutionGraph)
    assert isinstance(graph.acceptance_graph, AcceptanceExecutionGraph)

    assert report.statistics.draft_node_count > 0
    assert report.statistics.verification_node_count > 0
    assert report.statistics.acceptance_node_count > 0
