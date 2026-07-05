# SPDX-License-Identifier: Apache-2.0
"""
GraphScheduler verification testing.
Verifies invariants of the scheduling subsystem.
"""

import pytest
from unittest.mock import MagicMock
from collections import namedtuple

from omlx.runtime.scheduling.scheduler import GraphScheduler
from omlx.runtime.scheduling.policies import SchedulingPolicy
from omlx.runtime.scheduling.schedule import ExecutionSchedule

# Mock data structures for verification
MockGraph = namedtuple("MockGraph", ["operations"])
MockOp = namedtuple("MockOp", ["dependencies"])

def test_scheduler_consumes_backend_operation_graph_only():
    """Verify that GraphScheduler processes a valid graph structure to produce an ExecutionSchedule."""
    scheduler = GraphScheduler(policy=SchedulingPolicy.SEQUENTIAL)

    graph = MockGraph(operations={
        "op_1": MockOp(dependencies=[]),
        "op_2": MockOp(dependencies=["op_1"])
    })

    schedule = scheduler.build_schedule(graph)
    assert isinstance(schedule, ExecutionSchedule)
    assert len(schedule.ordered_operations) == 2
    assert "op_1" in schedule.ordered_operations
    assert "op_2" in schedule.ordered_operations

def test_scheduler_determinism():
    """Verify that providing the same graph multiple times produces identical schedules."""
    scheduler = GraphScheduler(policy=SchedulingPolicy.DEPENDENCY_DRIVEN)

    graph = MockGraph(operations={
        "C": MockOp(dependencies=["A", "B"]),
        "B": MockOp(dependencies=["A"]),
        "A": MockOp(dependencies=[])
    })

    schedule1 = scheduler.build_schedule(graph)
    schedule2 = scheduler.build_schedule(graph)
    schedule3 = scheduler.build_schedule(graph)

    assert schedule1.ordered_operations == schedule2.ordered_operations == schedule3.ordered_operations
    assert schedule1.ordered_operations == ["A", "B", "C"]

def test_execution_group_formation():
    """Verify that execution groups are formed correctly based on dependency levels."""
    scheduler = GraphScheduler(policy=SchedulingPolicy.DEPENDENCY_DRIVEN)

    # Graph: A -> B, A -> C (B and C can run in parallel, depend on A)
    graph = MockGraph(operations={
        "A": MockOp(dependencies=[]),
        "B": MockOp(dependencies=["A"]),
        "C": MockOp(dependencies=["A"])
    })

    schedule = scheduler.build_schedule(graph)
    assert len(schedule.execution_groups) == 2

    level_0 = next(g for g in schedule.execution_groups if g.dependency_level == 0)
    level_1 = next(g for g in schedule.execution_groups if g.dependency_level == 1)

    assert "A" in level_0.operations
    assert "B" in level_1.operations
    assert "C" in level_1.operations

    assert level_1.parallelizable is True
