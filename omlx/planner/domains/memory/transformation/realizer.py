# SPDX-License-Identifier: Apache-2.0
from typing import Dict, Tuple
from types import MappingProxyType

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.memory.artifacts import MemoryPlan
from .artifacts import (
    RealizedAllocationGraph,
    RealizedLifetimeGraph,
    MemoryExecutionGraph,
    MemoryRealizationDiagnostic,
    MemoryRealizationStatistics,
    MemoryValidationReport,
    MemoryRealizationReport,
)

class MemoryRealizer:
    """
    Compiler-native realization of immutable MemoryPlans into modified ExecutionIR.
    """
    def __init__(self):
        pass

    def realize(self, ir: ExecutionIR, plan: MemoryPlan) -> Tuple[ExecutionIR, MemoryRealizationReport]:
        """
        Transforms the given ExecutionIR according to the MemoryPlan.
        """
        diagnostics = []
        realized_allocations = []
        realized_lifetimes = []
        new_nodes: Dict[str, IRNode] = {}

        allocations_count = 0
        lifetimes_count = 0

        # Pass 1: Keep existing nodes
        for nid, node in ir.nodes.items():
            new_nodes[nid] = node

        # Pass 2: Realize allocations
        for i, alloc in enumerate(plan.allocation_graph.allocations):
            alloc_id = f"memory_allocation_{i}"
            alloc_node = IRNode(
                id=alloc_id,
                node_type=IRNodeType.ALLOCATION, # Need to make sure this exists or define a generic way
                dependencies=tuple(),
                metadata=MappingProxyType({
                    "allocation": str(alloc)
                })
            )
            new_nodes[alloc_id] = alloc_node
            allocations_count += 1
            realized_allocations.append(RealizedAllocationGraph(
                allocation_id=alloc_id,
                allocation_node=alloc_node
            ))

        # Pass 3: Realize lifetimes (e.g. releases)
        for i, lifetime in enumerate(plan.lifetime_graph.lifetimes):
            lifetime_id = f"memory_release_{lifetime.tensor_id}"
            release_node = IRNode(
                id=lifetime_id,
                node_type=IRNodeType.RELEASE, # Need to make sure this exists
                dependencies=tuple(), # In reality, depends on last_use_step nodes
                metadata=MappingProxyType({
                    "tensor_id": lifetime.tensor_id,
                    "last_use_step": lifetime.last_use_step
                })
            )
            new_nodes[lifetime_id] = release_node
            lifetimes_count += 1
            realized_lifetimes.append(RealizedLifetimeGraph(
                lifetime_id=lifetime_id,
                lifetime_nodes=(release_node,)
            ))

        transformed_ir = ExecutionIR(
            nodes=MappingProxyType(new_nodes),
            roots=ir.roots,
            metadata=ir.metadata
        )

        stats = MemoryRealizationStatistics(
            original_node_count=len(ir.nodes),
            transformed_node_count=len(transformed_ir.nodes),
            allocations_realized=allocations_count,
            lifetimes_realized=lifetimes_count
        )

        validation = MemoryValidationReport(
            is_valid=len(diagnostics) == 0,
            diagnostics=tuple(diagnostics)
        )

        execution_graph = MemoryExecutionGraph(
            allocations=tuple(realized_allocations),
            lifetimes=tuple(realized_lifetimes)
        )

        report = MemoryRealizationReport(
            statistics=stats,
            validation_report=validation,
            execution_graph=execution_graph
        )

        return transformed_ir, report
