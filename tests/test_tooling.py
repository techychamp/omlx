# SPDX-License-Identifier: Apache-2.0
import pytest
from types import MappingProxyType
from omlx.tooling.inspector.inspector import CompilerInspector
from omlx.tooling.export.json_exporter import JsonExporter
from omlx.tooling.export.mermaid_exporter import MermaidExporter
from omlx.tooling.views.graph_views import to_value_graph
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType

def test_inspector_logical_ir():
    inspector = CompilerInspector()
    node = IRNode("n1", IRNodeType.FORWARD, dependencies=tuple())
    ir = ExecutionIR(nodes=MappingProxyType({"n1": node}), roots=("n1",))

    result = inspector.inspect_logical_ir(ir)
    assert "nodes" in result
    assert "n1" in result["nodes"]

def test_json_exporter():
    exporter = JsonExporter()
    data = {"test": 123, "list": [1, 2]}
    res = exporter.export(data)
    assert '"test": 123' in res

def test_mermaid_exporter():
    exporter = MermaidExporter()
    data = {
        "nodes": {"A": {"label": "Node A"}, "B": {"label": "Node B"}},
        "edges": [{"source": "A", "target": "B", "label": "dep"}]
    }
    res = exporter.export(data)
    assert "graph TD" in res
    assert 'A["Node A"]' in res
    assert 'A -- "dep" --> B' in res

def test_graph_views():
    node = IRNode("n1", IRNodeType.FORWARD, dependencies=("n0",))
    ir = ExecutionIR(nodes=MappingProxyType({"n1": node}), roots=("n1",))

    graph = to_value_graph(ir)
    assert "nodes" in graph
    assert "n1" in graph["nodes"]
    assert "edges" in graph
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["source"] == "n0"
