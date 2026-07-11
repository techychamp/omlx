from typing import Dict, List, Set, Optional, Tuple
from types import MappingProxyType

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionGroup
from .artifacts import (
    RealizedFusionGroup,
    TransformationDiagnostic,
    TransformationStatistics,
    TransformationValidationReport,
    TransformationReport,
)

class FusionRealizer:
    """
    Compiler-native realization of immutable FusionPlans into modified ExecutionIR.
    Transforms the ExecutionIR graph while preserving semantics.
    """
    def __init__(self):
        pass

    def realize(self, ir: ExecutionIR, plan: FusionPlan) -> Tuple[ExecutionIR, TransformationReport]:
        """
        Transforms the given ExecutionIR according to the FusionPlan.
        Returns the transformed graph and a detailed transformation report.
        """
        diagnostics = []
        realized_groups = []

        # We need to construct a new graph by replacing fused nodes.
        new_nodes: Dict[str, IRNode] = {}
        # Keep track of old node ID to new fused node ID mapping
        node_remap: Dict[str, str] = {}

        for group in plan.groups:
            # 1. Validate that all nodes exist in the current IR
            missing_nodes = [nid for nid in group.node_ids if nid not in ir.nodes]
            if missing_nodes:
                diagnostics.append(TransformationDiagnostic(
                    level="ERROR",
                    message=f"Nodes missing from IR for fusion group {group.id}",
                    metadata=MappingProxyType({"missing": tuple(missing_nodes)})
                ))
                continue

            # 2. Create the new fused node
            fused_id = f"fused_{group.id}"

            # Combine dependencies. A fused node depends on the union of all
            # dependencies of its constituent nodes, EXCEPT for dependencies
            # that are also within the fusion group (internal edges).
            new_deps: Set[str] = set()
            for nid in group.node_ids:
                for dep in ir.nodes[nid].dependencies:
                    if dep not in group.node_ids:
                        new_deps.add(dep)

            # Use IRNodeType.FORWARD as a generic type for fused operations,
            # or a more specific type if we add one for fusion.
            fused_node = IRNode(
                id=fused_id,
                node_type=IRNodeType.FORWARD,
                dependencies=tuple(new_deps),
                metadata=MappingProxyType({
                    "fused_from": tuple(group.node_ids),
                    "fusion_type": group.fusion_type
                })
            )

            new_nodes[fused_id] = fused_node

            for nid in group.node_ids:
                node_remap[nid] = fused_id

            realized_groups.append(RealizedFusionGroup(
                id=group.id,
                original_node_ids=tuple(group.node_ids),
                fused_node=fused_node,
                fusion_type=group.fusion_type
            ))

        # 3. Process remaining nodes and rewire dependencies
        for nid, node in ir.nodes.items():
            if nid in node_remap:
                continue # Skip nodes that were fused away

            # Rewire dependencies
            new_deps = []
            for dep in node.dependencies:
                # If a dependency was fused, point to the new fused node
                if dep in node_remap:
                    new_dep = node_remap[dep]
                    if new_dep not in new_deps: # Avoid duplicates
                        new_deps.append(new_dep)
                else:
                    new_deps.append(dep)

            new_nodes[nid] = IRNode(
                id=node.id,
                node_type=node.node_type,
                dependencies=tuple(new_deps),
                metadata=node.metadata
            )

        # 4. Rewire roots
        new_roots = []
        for root in ir.roots:
            if root in node_remap:
                new_root = node_remap[root]
                if new_root not in new_roots:
                    new_roots.append(new_root)
            else:
                new_roots.append(root)

        transformed_ir = ExecutionIR(
            nodes=MappingProxyType(new_nodes),
            roots=tuple(new_roots),
            metadata=MappingProxyType(dict(ir.metadata))
        )

        nodes_fused = sum(len(g.node_ids) for g in plan.groups if all(nid in ir.nodes for nid in g.node_ids))

        stats = TransformationStatistics(
            original_node_count=len(ir.nodes),
            transformed_node_count=len(transformed_ir.nodes),
            nodes_fused=nodes_fused,
            groups_realized=len(realized_groups)
        )

        validation = TransformationValidationReport(
            is_valid=len(diagnostics) == 0,
            diagnostics=tuple(diagnostics)
        )

        report = TransformationReport(
            statistics=stats,
            validation_report=validation,
            realized_groups=tuple(realized_groups)
        )

        return transformed_ir, report
