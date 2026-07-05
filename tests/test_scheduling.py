# SPDX-License-Identifier: Apache-2.0
"""
Tests for OMLX Scheduling subsystem.
"""

import pytest
import concurrent.futures
from dataclasses import dataclass
from typing import List, Dict

from omlx.runtime.scheduling.scheduler import GraphScheduler
from omlx.runtime.scheduling.policies import SchedulingPolicy
from omlx.runtime.scheduling.dependency import DependencyAnalyzer
from omlx.runtime.scheduling.critical_path import CriticalPathAnalyzer
from omlx.runtime.execution.graph_executor import DeterministicGraphExecutor
from omlx.runtime.execution.context import ExecutionContext

@dataclass
class MockOp:
    dependencies: List[str]

@dataclass
class MockGraph:
    operations: Dict[str, MockOp]

class MockDispatcher:
    def dispatch(self, graph, context, execution_order=None):
        from omlx.runtime.execution.types import ExecutionResult, ExecutionStatus
        return ExecutionResult(status=ExecutionStatus.COMPLETED, model_output={"order": execution_order})

def test_linear_graph():
    graph = MockGraph({
        "A": MockOp([]),
        "B": MockOp(["A"]),
        "C": MockOp(["B"])
    })
    scheduler = GraphScheduler(SchedulingPolicy.DEPENDENCY_DRIVEN)
    schedule = scheduler.build_schedule(graph)
    assert schedule.ordered_operations == ["A", "B", "C"]
    assert schedule.statistics.graph_depth == 3
    assert schedule.statistics.critical_path_length == 3

def test_branching_graph():
    graph = MockGraph({
        "A": MockOp([]),
        "B": MockOp(["A"]),
        "C": MockOp(["A"]),
        "D": MockOp(["B", "C"])
    })
    scheduler = GraphScheduler(SchedulingPolicy.DEPENDENCY_DRIVEN)
    schedule = scheduler.build_schedule(graph)
    assert schedule.ordered_operations[0] == "A"
    assert set(schedule.ordered_operations[1:3]) == {"B", "C"}
    assert schedule.ordered_operations[3] == "D"
    assert schedule.statistics.graph_depth == 3
    assert schedule.statistics.critical_path_length == 3
    assert len(schedule.execution_groups) == 3 # A, [B,C], D
    assert schedule.execution_groups[1].parallelizable == True

def test_isolated_nodes():
    graph = MockGraph({
        "A": MockOp([]),
        "B": MockOp([])
    })
    scheduler = GraphScheduler(SchedulingPolicy.DEPENDENCY_DRIVEN)
    schedule = scheduler.build_schedule(graph)
    assert set(schedule.ordered_operations) == {"A", "B"}
    assert schedule.statistics.graph_depth == 1
    assert schedule.statistics.critical_path_length == 1
    assert len(schedule.execution_groups) == 1
    assert schedule.execution_groups[0].parallelizable == True

def test_cyclic_graph():
    graph = MockGraph({
        "A": MockOp(["B"]),
        "B": MockOp(["A"])
    })
    scheduler = GraphScheduler(SchedulingPolicy.DEPENDENCY_DRIVEN)
    schedule = scheduler.build_schedule(graph)
    # the scheduler should handle cycles gracefully by identifying valid subsets or an empty set
    assert len(schedule.ordered_operations) < 2
    assert schedule.diagnostics.dependency_report["is_cyclic"] == True

def test_thread_safety():
    graph = MockGraph({
        "A": MockOp([]),
        "B": MockOp(["A"]),
        "C": MockOp(["A"]),
        "D": MockOp(["B", "C"])
    })
    scheduler = GraphScheduler(SchedulingPolicy.DEPENDENCY_DRIVEN)

    def generate_schedule():
        return scheduler.build_schedule(graph)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(generate_schedule) for _ in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    for r in results:
         assert r.ordered_operations[0] == "A"
         assert r.ordered_operations[3] == "D"

def test_graph_executor_integration():
    graph = MockGraph({
        "A": MockOp([]),
        "B": MockOp(["A"]),
        "C": MockOp(["B"])
    })
    dispatcher = MockDispatcher()
    executor = DeterministicGraphExecutor(dispatcher)
    result = executor.traverse_and_execute(graph, ExecutionContext())
    assert result.model_output["order"] == ["A", "B", "C"]
    assert result.statistics.graph_depth == 3
    assert result.statistics.execution_groups == 3
