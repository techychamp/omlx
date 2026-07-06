# SPDX-License-Identifier: Apache-2.0
"""
GraphScheduler for OMLX Scheduling subsystem.
Produces immutable execution schedules from BackendOperationGraph or DependencyGraph.
"""

import time
import logging
from typing import List, Dict, Any, Union

from .interfaces import GraphScheduler as IGraphScheduler
from .types import BackendOperationGraph
from .artifacts import DependencyGraph
from .schedule import ExecutionSchedule
from .group import ExecutionGroup
from .policies import SchedulingPolicy
from .analyzer import GraphAnalyzer
from .diagnostics import SchedulingDiagnostics
from .statistics import SchedulingStatistics

logger = logging.getLogger("omlx.scheduling.scheduler")

class GraphScheduler(IGraphScheduler):
    """
    Analyzes dependency graphs and builds an ExecutionSchedule.
    """
    def __init__(self, policy: SchedulingPolicy = SchedulingPolicy.DEPENDENCY_DRIVEN):
        self.policy = policy
        self.analyzer = GraphAnalyzer()

    def build_schedule(self, graph: Union[BackendOperationGraph, DependencyGraph]) -> ExecutionSchedule:
        start_time = time.time()
        logger.debug(f"Building schedule with policy {self.policy}")

        if not graph or not hasattr(graph, 'operations') or not graph.operations:
            return ExecutionSchedule(
                statistics=SchedulingStatistics(schedule_generation_time_ms=(time.time() - start_time) * 1000)
            )

        if isinstance(graph, DependencyGraph):
             return self._build_from_dependency_graph(graph, start_time)
        else:
             return self._build_from_backend_graph(graph, start_time)

    def _build_from_dependency_graph(self, graph: DependencyGraph, start_time: float) -> ExecutionSchedule:
        # Multi-plan dependency execution support
        ordered_operations: List[str] = []
        execution_groups: List[ExecutionGroup] = []
        ready_queues: Dict[int, List[str]] = {}

        # Build a unified operations dict mapped to phases
        op_phase_map = {}
        for phase_idx, phase in enumerate(graph.phases):
            for op in phase.operations:
                op_phase_map[op] = phase_idx

        # Simple policy: sequence phases
        for phase_idx, phase in enumerate(graph.phases):
             ops = list(phase.operations)
             ops.sort() # Ensure deterministic ordering
             ordered_operations.extend(ops)
             ready_queues[phase_idx] = ops
             execution_groups.append(ExecutionGroup(
                 group_id=f"phase_{phase_idx}_{phase.name}",
                 operations=ops,
                 dependency_level=phase_idx,
                 parallelizable=len(ops) > 1
             ))

        # Support fallback if phases are not explicitly defined
        if not graph.phases and graph.operations:
             ops = list(graph.operations.keys())
             ops.sort()
             ordered_operations.extend(ops)
             ready_queues[0] = ops
             execution_groups.append(ExecutionGroup(
                 group_id="group_0",
                 operations=ops,
                 dependency_level=0,
                 parallelizable=True
             ))

        num_levels = len(ready_queues) if ready_queues else 1
        max_width = max([len(ops) for ops in ready_queues.values()]) if ready_queues else 1
        parallel_groups = sum(1 for g in execution_groups if g.parallelizable)
        estimated_parallelism = len(ordered_operations) / num_levels if num_levels > 0 else 0

        stats = SchedulingStatistics(
            graph_depth=len(graph.phases) if graph.phases else 1,
            graph_width=max_width,
            critical_path_length=len(graph.phases) if graph.phases else 1,
            dependency_fan_in=1.0,
            dependency_fan_out=1.0,
            parallel_groups=parallel_groups,
            execution_levels=num_levels,
            estimated_parallelism=estimated_parallelism,
            schedule_generation_time_ms=(time.time() - start_time) * 1000
        )

        diagnostics = SchedulingDiagnostics(
             scheduling_report={"status": "success", "policy": self.policy.value, "type": "DependencyGraph"},
             dependency_report={"roots": [], "leaves": [], "is_cyclic": False},
             critical_path_report={"path": [], "length": len(graph.phases)},
             execution_group_report={"groups_count": len(execution_groups)},
             parallelism_report={"estimated": estimated_parallelism},
             policy_report={"active_policy": self.policy.value},
             execution_ordering_report={"operations_count": len(ordered_operations)}
        )

        return ExecutionSchedule(
            ordered_operations=ordered_operations,
            dependency_levels={op: phase_idx for op, phase_idx in op_phase_map.items()},
            execution_groups=execution_groups,
            critical_path=[],
            ready_queues=ready_queues,
            metadata={"policy": self.policy.value},
            diagnostics=diagnostics,
            statistics=stats
        )

    def _build_from_backend_graph(self, graph: BackendOperationGraph, start_time: float) -> ExecutionSchedule:
        # 1. Analyze
        dep_result, cp_result = self.analyzer.analyze(graph)

        # 2. Build execution order based on policy
        ordered_operations: List[str] = []
        ready_queues: Dict[int, List[str]] = {}
        execution_groups: List[ExecutionGroup] = []

        if self.policy == SchedulingPolicy.SEQUENTIAL:
            # Fallback to simple traversal or given order
            # Using the roots from dep_result
            queue = list(dep_result.roots)
            in_degrees = dict(dep_result.in_degrees)
            adj_list = {op_id: [] for op_id in graph.operations}
            for op_id, op in graph.operations.items():
                for dep_id in op.dependencies:
                    if dep_id in adj_list:
                        adj_list[dep_id].append(op_id)

            while queue:
                queue.sort() # Ensure deterministic ordering
                curr = queue.pop(0)
                ordered_operations.append(curr)
                for neighbor in adj_list.get(curr, []):
                    in_degrees[neighbor] -= 1
                    if in_degrees[neighbor] == 0:
                        queue.append(neighbor)

            # Create a single group
            if ordered_operations:
                 execution_groups.append(ExecutionGroup(
                     group_id="group_0",
                     operations=list(ordered_operations),
                     dependency_level=0
                 ))

        else:
            # DEPENDENCY_DRIVEN (default for now)
            # Group by dependency levels
            levels = dep_result.levels
            # Create groups per level
            level_groups: Dict[int, List[str]] = {}
            for op_id, level in levels.items():
                if level not in level_groups:
                    level_groups[level] = []
                level_groups[level].append(op_id)

            for level in sorted(level_groups.keys()):
                ops = sorted(level_groups[level]) # deterministic
                ready_queues[level] = ops
                ordered_operations.extend(ops)
                execution_groups.append(ExecutionGroup(
                     group_id=f"group_{level}",
                     operations=ops,
                     dependency_level=level,
                     parallelizable=len(ops) > 1
                ))

        # 3. Statistics
        num_levels = len(ready_queues) if ready_queues else 1
        max_width = max([len(ops) for ops in ready_queues.values()]) if ready_queues else 1
        parallel_groups = sum(1 for g in execution_groups if g.parallelizable)
        estimated_parallelism = len(ordered_operations) / num_levels if num_levels > 0 else 0

        stats = SchedulingStatistics(
            graph_depth=dep_result.graph_depth,
            graph_width=max_width,
            critical_path_length=cp_result.length,
            dependency_fan_in=dep_result.avg_fan_in,
            dependency_fan_out=dep_result.avg_fan_out,
            parallel_groups=parallel_groups,
            execution_levels=num_levels,
            estimated_parallelism=estimated_parallelism,
            schedule_generation_time_ms=(time.time() - start_time) * 1000
        )

        # 4. Diagnostics
        diagnostics = SchedulingDiagnostics(
             scheduling_report={"status": "success", "policy": self.policy.value, "type": "BackendOperationGraph"},
             dependency_report={"roots": dep_result.roots, "leaves": dep_result.leaves, "is_cyclic": dep_result.is_cyclic},
             critical_path_report={"path": cp_result.path, "length": cp_result.length},
             execution_group_report={"groups_count": len(execution_groups)},
             parallelism_report={"estimated": estimated_parallelism},
             policy_report={"active_policy": self.policy.value},
             execution_ordering_report={"operations_count": len(ordered_operations)}
        )

        return ExecutionSchedule(
            ordered_operations=ordered_operations,
            dependency_levels=dep_result.levels,
            execution_groups=execution_groups,
            critical_path=cp_result.path,
            ready_queues=ready_queues,
            metadata={"policy": self.policy.value},
            diagnostics=diagnostics,
            statistics=stats
        )
