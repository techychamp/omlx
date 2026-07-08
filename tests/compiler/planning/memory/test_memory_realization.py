# SPDX-License-Identifier: Apache-2.0

import pytest
from typing import Dict, Any
from types import MappingProxyType

from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.domains.memory.artifacts import (
    MemoryPlan, MemoryDescriptor, MemoryRequirement, AllocationGraph, LifetimeGraph, TensorLifetime
)
from omlx.planner.domains.memory.transformation.realizer import MemoryRealizer
from omlx.planner.domains.memory.transformation.validator import MemoryTransformationValidator
from omlx.planner.domains.memory.transformation.pass_ import MemoryRealizationPass

def test_memory_realizer():
    # Setup initial IR
    nodes = {
        "node1": IRNode(id="node1", node_type=IRNodeType.FORWARD),
        "node2": IRNode(id="node2", node_type=IRNodeType.FORWARD, dependencies=("node1",))
    }
    ir = ExecutionIR(nodes=MappingProxyType(nodes), roots=("node1",))

    # Setup MemoryPlan
    alloc_graph = AllocationGraph(allocations=["alloc_tensor_A", "alloc_tensor_B"])
    lifetime_graph = LifetimeGraph(lifetimes=[
        TensorLifetime(tensor_id="tensor_A", creation_step=0, last_use_step=1, size_bytes=1024),
        TensorLifetime(tensor_id="tensor_B", creation_step=1, last_use_step=2, size_bytes=2048)
    ])

    plan = MemoryPlan(
        descriptor=MemoryDescriptor(0, 0),
        requirement=MemoryRequirement(0, 0),
        allocation_graph=alloc_graph,
        lifetime_graph=lifetime_graph
    )

    realizer = MemoryRealizer()
    transformed_ir, report = realizer.realize(ir, plan)

    assert report.validation_report.is_valid
    assert len(transformed_ir.nodes) == len(nodes) + 2 + 2 # Original + 2 allocations + 2 releases

    assert report.statistics.allocations_realized == 2
    assert report.statistics.lifetimes_realized == 2

    # Verify nodes
    alloc_nodes = [n for n in transformed_ir.nodes.values() if n.node_type == IRNodeType.ALLOCATION]
    release_nodes = [n for n in transformed_ir.nodes.values() if n.node_type == IRNodeType.RELEASE]

    assert len(alloc_nodes) == 2
    assert len(release_nodes) == 2

def test_memory_realization_pass():
    # Setup initial IR
    nodes = {
        "node1": IRNode(id="node1", node_type=IRNodeType.FORWARD)
    }
    ir = ExecutionIR(nodes=MappingProxyType(nodes), roots=("node1",))

    # Setup MemoryPlan
    alloc_graph = AllocationGraph(allocations=["alloc_tensor_A"])
    lifetime_graph = LifetimeGraph(lifetimes=[
        TensorLifetime(tensor_id="tensor_A", creation_step=0, last_use_step=1, size_bytes=1024)
    ])

    plan = MemoryPlan(
        descriptor=MemoryDescriptor(0, 0),
        requirement=MemoryRequirement(0, 0),
        allocation_graph=alloc_graph,
        lifetime_graph=lifetime_graph
    )

    pass_ = MemoryRealizationPass(plan)
    transformed_ir = pass_.apply(ir)

    assert len(transformed_ir.nodes) == 1 + 1 + 1 # 1 original, 1 alloc, 1 release
    assert pass_.report is not None
    assert pass_.report.validation_report.is_valid
