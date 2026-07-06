# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List, Set, Tuple
from types import MappingProxyType

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.moe.artifacts import MoEPlan
from .artifacts import (
    RealizedExpertGraph,
    ExpertRoutingGraph,
    ExpertExecutionGraph,
    ExpertRealizationDiagnostic,
    ExpertRealizationStatistics,
    ExpertValidationReport,
    ExpertRealizationReport,
)

class MoERealizer:
    """
    Compiler-native realization of immutable MoEPlans into modified ExecutionIR.
    """
    def __init__(self):
        pass

    def realize(self, ir: ExecutionIR, plan: MoEPlan) -> Tuple[ExecutionIR, ExpertRealizationReport]:
        """
        Transforms the given ExecutionIR according to the MoEPlan.
        """
        diagnostics = []
        realized_groups = []
        new_nodes: Dict[str, IRNode] = {}
        node_remap: Dict[str, str] = {}

        experts_realized = 0

        # Pass 1: Keep existing nodes
        for nid, node in ir.nodes.items():
            new_nodes[nid] = node

        # Pass 2: Realize groups
        for group in plan.groups:
            expert_graphs = []
            expert_fwd_nodes = []

            # Generate expert nodes
            for expert in group.experts:
                expert_node_id = f"moe_expert_{group.id}_{expert.id}"

                expert_node = IRNode(
                    id=expert_node_id,
                    node_type=IRNodeType.FORWARD,
                    dependencies=tuple(), # Will be updated
                    metadata=MappingProxyType({
                        "expert_id": expert.id,
                        "group_id": group.id,
                        "moe_metadata": expert.metadata
                    })
                )

                new_nodes[expert_node_id] = expert_node
                experts_realized += 1
                expert_fwd_nodes.append(expert_node)

                expert_graphs.append(RealizedExpertGraph(
                    expert_id=expert.id,
                    expert_nodes=(expert_node,)
                ))

            # Create routing node
            routing_id = f"moe_routing_{group.id}"

            routing_node = IRNode(
                id=routing_id,
                node_type=IRNodeType.ROUTING,
                dependencies=tuple(),
                metadata=MappingProxyType({
                    "group_id": group.id,
                    "experts": tuple(e.id for e in group.experts)
                })
            )

            new_nodes[routing_id] = routing_node

            # Update expert dependencies to depend on routing
            for expert_node in expert_fwd_nodes:
                updated_node = IRNode(
                    id=expert_node.id,
                    node_type=expert_node.node_type,
                    dependencies=(routing_id,),
                    metadata=expert_node.metadata
                )
                new_nodes[updated_node.id] = updated_node

            # Update RealizedExpertGraph with updated node
            updated_expert_graphs = []
            for eg in expert_graphs:
                updated_nodes = tuple(new_nodes[n.id] for n in eg.expert_nodes)
                updated_expert_graphs.append(RealizedExpertGraph(
                    expert_id=eg.expert_id,
                    expert_nodes=updated_nodes
                ))

            routing_graph = ExpertRoutingGraph(
                routing_id=routing_id,
                routing_node=routing_node,
                expert_graphs=tuple(updated_expert_graphs)
            )

            execution_graph = ExpertExecutionGraph(
                group_id=group.id,
                routing_graph=routing_graph
            )

            realized_groups.append(execution_graph)

        transformed_ir = ExecutionIR(
            nodes=MappingProxyType(new_nodes),
            roots=ir.roots,
            metadata=ir.metadata
        )

        stats = ExpertRealizationStatistics(
            original_node_count=len(ir.nodes),
            transformed_node_count=len(transformed_ir.nodes),
            experts_realized=experts_realized,
            groups_realized=len(realized_groups)
        )

        validation = ExpertValidationReport(
            is_valid=len(diagnostics) == 0,
            diagnostics=tuple(diagnostics)
        )

        report = ExpertRealizationReport(
            statistics=stats,
            validation_report=validation,
            realized_groups=tuple(realized_groups)
        )

        return transformed_ir, report
