# SPDX-License-Identifier: Apache-2.0

import pytest
from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.analysis.analyzer import GraphAnalyzer
from omlx.planner.ir.analysis.artifacts import DiagnosticLevel

@pytest.fixture
def valid_ir():
    nodes = {
        "node_a": IRNode(id="node_a", node_type=IRNodeType.PREFILL),
        "node_b": IRNode(id="node_b", node_type=IRNodeType.FORWARD, dependencies=("node_a",)),
        "node_c": IRNode(id="node_c", node_type=IRNodeType.SAMPLE, dependencies=("node_b",)),
    }
    return ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("node_c",)
    )

@pytest.fixture
def ir_with_cycle():
    nodes = {
        "node_a": IRNode(id="node_a", node_type=IRNodeType.PREFILL, dependencies=("node_c",)),
        "node_b": IRNode(id="node_b", node_type=IRNodeType.FORWARD, dependencies=("node_a",)),
        "node_c": IRNode(id="node_c", node_type=IRNodeType.SAMPLE, dependencies=("node_b",)),
    }
    return ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("node_c",)
    )

@pytest.fixture
def ir_with_unreachable():
    nodes = {
        "node_a": IRNode(id="node_a", node_type=IRNodeType.PREFILL),
        "node_b": IRNode(id="node_b", node_type=IRNodeType.FORWARD, dependencies=("node_a",)),
        "node_c": IRNode(id="node_c", node_type=IRNodeType.SAMPLE, dependencies=("node_b",)),
        "unreachable": IRNode(id="unreachable", node_type=IRNodeType.VERIFY),
    }
    return ExecutionIR(
        nodes=MappingProxyType(nodes),
        roots=("node_c",)
    )

def test_analyze_valid_graph(valid_ir):
    analyzer = GraphAnalyzer()
    report = analyzer.analyze(valid_ir)

    assert report.validation.is_valid is True
    assert len(report.validation.diagnostics) == 0

    assert report.statistics.node_count == 3
    assert report.statistics.edge_count == 2
    assert report.statistics.max_depth == 3

    assert not report.dependencies.has_cycles
    assert report.dependencies.dependencies["node_b"] == ("node_a",)
    assert report.dependencies.dependents["node_a"] == ("node_b",)

    assert report.critical_path.estimated_cost == 3.0
    assert report.critical_path.path_nodes == ("node_c", "node_b", "node_a")

def test_analyze_graph_with_cycle(ir_with_cycle):
    analyzer = GraphAnalyzer()
    report = analyzer.analyze(ir_with_cycle)

    assert report.validation.is_valid is False
    assert any(diag.message == "Cycle detected in graph dependencies." for diag in report.validation.diagnostics)
    assert report.dependencies.has_cycles is True

def test_analyze_graph_with_unreachable(ir_with_unreachable):
    analyzer = GraphAnalyzer()
    report = analyzer.analyze(ir_with_unreachable)

    assert report.validation.is_valid is False
    assert any("Unreachable nodes detected: unreachable" in diag.message for diag in report.validation.diagnostics)

def test_graph_traversal(valid_ir):
    analyzer = GraphAnalyzer()
    traversal = analyzer.traverse(valid_ir)

    # Dependencies should be visited first in post-order traversal
    assert traversal.traversal_order == ("node_a", "node_b", "node_c")
    assert len(traversal.unreachable_nodes) == 0
