import pytest
from types import MappingProxyType
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.moe.transformation.artifacts import (
    RealizedExpertGraph,
    ExpertRoutingGraph,
    ExpertExecutionGraph
)
from omlx.runtime.execution.engine import ExecutionEngine
from omlx.runtime.execution.context import ExecutionContext
from omlx.runtime.session import RuntimeSession

class MockAdapter:
    def execute(self, op, context):
        if op.node_type == IRNodeType.ROUTING:
            return {"result": {"active_experts": ["e1", "e2"], "weights": [0.6, 0.4]}}
        elif op.node_type == IRNodeType.FORWARD:
            if op.id == "e1":
                return {"result": {"logits": [10, 20, 30], "expert_id": op.metadata.get("expert_id")}}
            else:
                return {"result": {"logits": [1, 2, 3], "expert_id": op.metadata.get("expert_id")}}
        return {"result": {}}

def test_moe_execution_engine():
    # Setup mock MoE graph
    e1 = IRNode(id="e1", node_type=IRNodeType.FORWARD, dependencies=("r1",), metadata=MappingProxyType({"expert_id": "e1"}))
    e2 = IRNode(id="e2", node_type=IRNodeType.FORWARD, dependencies=("r1",), metadata=MappingProxyType({"expert_id": "e2"}))
    
    r1 = IRNode(id="r1", node_type=IRNodeType.ROUTING, dependencies=(), metadata=MappingProxyType({"group_id": "g1", "aggregation": "weighted_merge"}))
    
    routing_graph = ExpertRoutingGraph(
        routing_id="r1",
        routing_node=r1,
        expert_graphs=(
            RealizedExpertGraph("e1", (e1,)),
            RealizedExpertGraph("e2", (e2,))
        )
    )
    
    moe_graph = ExpertExecutionGraph(group_id="g1", routing_graph=routing_graph)
    
    session = RuntimeSession.create()
    session.expert_execution_graph = moe_graph
    
    context = ExecutionContext(
        expert_execution_graph=moe_graph,
        adapter=MockAdapter()
    )
    session.execution_context = context
    
    engine = ExecutionEngine()
    result = engine.execute(session)
    
    assert result.status.value == "completed"
    assert "last_output" in result.model_output
    assert result.model_output["last_output"]["result"]["aggregated"] is True
    assert result.model_output["last_output"]["result"]["method"] == "weighted_merge"
    
    logits = result.model_output["last_output"]["result"]["logits"]
    # 10*0.6 + 1*0.4 = 6.4
    # 20*0.6 + 2*0.4 = 12.8
    # 30*0.6 + 3*0.4 = 19.2
    assert abs(logits[0] - 6.4) < 1e-5
    assert abs(logits[1] - 12.8) < 1e-5
    assert abs(logits[2] - 19.2) < 1e-5

def test_moe_dispatcher_top_k():
    class TopKAdapter:
        def execute(self, op, context):
            if op.node_type == IRNodeType.ROUTING:
                return {"result": {"active_experts": ["e2"], "weights": [1.0]}}
            elif op.node_type == IRNodeType.FORWARD:
                if op.id == "e2":
                    return {"result": {"logits": [100, 200, 300], "expert_id": op.metadata.get("expert_id")}}
            return {"result": {}}

    e1 = IRNode(id="e1", node_type=IRNodeType.FORWARD, dependencies=("r1",), metadata=MappingProxyType({"expert_id": "e1"}))
    e2 = IRNode(id="e2", node_type=IRNodeType.FORWARD, dependencies=("r1",), metadata=MappingProxyType({"expert_id": "e2"}))
    
    r1 = IRNode(id="r1", node_type=IRNodeType.ROUTING, dependencies=(), metadata=MappingProxyType({"group_id": "g1", "aggregation": "top-k merge"}))
    
    routing_graph = ExpertRoutingGraph(
        routing_id="r1",
        routing_node=r1,
        expert_graphs=(
            RealizedExpertGraph("e1", (e1,)),
            RealizedExpertGraph("e2", (e2,))
        )
    )
    
    moe_graph = ExpertExecutionGraph(group_id="g1", routing_graph=routing_graph)
    
    session = RuntimeSession.create()
    session.expert_execution_graph = moe_graph
    
    context = ExecutionContext(
        expert_execution_graph=moe_graph,
        adapter=TopKAdapter()
    )
    session.execution_context = context
    
    engine = ExecutionEngine()
    result = engine.execute(session)
    
    assert result.status.value == "completed"
    assert result.model_output["last_output"]["result"]["aggregated"] is True
    assert result.model_output["last_output"]["result"]["method"] == "top-k merge"
    
    logits = result.model_output["last_output"]["result"]["logits"]
    assert logits == [100, 200, 300]
