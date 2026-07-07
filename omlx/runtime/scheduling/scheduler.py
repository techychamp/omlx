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
from .artifacts import ExecutionPhaseGraph
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

    def build_schedule(self, graph: Union[BackendOperationGraph, DependencyGraph, ExecutionPhaseGraph]) -> ExecutionSchedule:
        start_time = time.time()
        logger.debug(f"Building schedule with policy {self.policy}")

        if not graph:
            return ExecutionSchedule(
                statistics=SchedulingStatistics(schedule_generation_time_ms=(time.time() - start_time) * 1000)
            )

        has_ops = hasattr(graph, 'operations') and graph.operations
        has_moe = type(graph).__name__ == 'ExpertExecutionGraph' and hasattr(graph, 'routing_graph')

        if not has_ops and not has_moe:
            return ExecutionSchedule(
                statistics=SchedulingStatistics(schedule_generation_time_ms=(time.time() - start_time) * 1000)
            )

        if isinstance(graph, ExecutionPhaseGraph):
             return self._build_from_execution_phase_graph(graph, start_time)
        elif isinstance(graph, DependencyGraph):
             return self._build_from_dependency_graph(graph, start_time)
        elif type(graph).__name__ == 'ExpertExecutionGraph':
             return self._build_from_expert_graph(graph, start_time)
        else:
             return self._build_from_backend_graph(graph, start_time)

    def _build_from_dependency_graph(self, graph: DependencyGraph, start_time: float) -> ExecutionSchedule:
        # Multi-plan dependency execution support
        ordered_operations: List[str] = []
        execution_groups: List[ExecutionGroup] = []
        ready_queues: Dict[int, Tuple[str, ...]] = {}

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
             ready_queues[phase_idx] = tuple(ops)
             execution_groups.append(ExecutionGroup(
                 group_id=f"phase_{phase_idx}_{phase.name}",
                 operations=tuple(ops),
                 dependency_level=phase_idx,
                 parallelizable=len(ops) > 1
             ))

        # Support fallback if phases are not explicitly defined
        if not graph.phases and graph.operations:
             ops = list(graph.operations.keys())
             ops.sort()
             ordered_operations.extend(ops)
             ready_queues[0] = tuple(ops)
             execution_groups.append(ExecutionGroup(
                 group_id="group_0",
                 operations=tuple(ops),
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
            ordered_operations=tuple(ordered_operations),
            dependency_levels={op: phase_idx for op, phase_idx in op_phase_map.items()},
            execution_groups=tuple(execution_groups),
            critical_path=tuple(),
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
        ready_queues: Dict[int, Tuple[str, ...]] = {}
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
                     operations=tuple(ordered_operations),
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
                ready_queues[level] = tuple(ops)
                ordered_operations.extend(ops)
                execution_groups.append(ExecutionGroup(
                     group_id=f"group_{level}",
                     operations=tuple(ops),
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
            ordered_operations=tuple(ordered_operations),
            dependency_levels=dep_result.levels,
            execution_groups=tuple(execution_groups),
            critical_path=tuple(cp_result.path),
            ready_queues=ready_queues,
            metadata={"policy": self.policy.value},
            diagnostics=diagnostics,
            statistics=stats
        )

    def _build_from_execution_phase_graph(self, graph: ExecutionPhaseGraph, start_time: float) -> ExecutionSchedule:
        ordered_operations: List[str] = []
        execution_groups: List[ExecutionGroup] = []
        ready_queues: Dict[int, Tuple[str, ...]] = {}

        op_phase_map = {}
        for phase_idx, phase in enumerate(graph.phases):
            for op in phase.operations:
                op_phase_map[op] = phase_idx

        for phase_idx, phase in enumerate(graph.phases):
             ops = list(phase.operations)
             ops.sort() # Ensure deterministic ordering
             ordered_operations.extend(ops)
             ready_queues[phase_idx] = tuple(ops)
             execution_groups.append(ExecutionGroup(
                 group_id=f"phase_{phase_idx}_{phase.name}",
                 operations=tuple(ops),
                 dependency_level=phase_idx,
                 parallelizable=len(ops) > 1
             ))

        num_levels = len(ready_queues) if ready_queues else 1
        max_width = max([len(ops) for ops in ready_queues.values()]) if ready_queues else 1
        parallel_groups = sum(1 for g in execution_groups if g.parallelizable)
        estimated_parallelism = len(ordered_operations) / num_levels if num_levels > 0 else 0

        stats = SchedulingStatistics(
            graph_depth=len(graph.phases),
            graph_width=max_width,
            critical_path_length=len(graph.phases),
            dependency_fan_in=1.0,
            dependency_fan_out=1.0,
            parallel_groups=parallel_groups,
            execution_levels=num_levels,
            estimated_parallelism=estimated_parallelism,
            schedule_generation_time_ms=(time.time() - start_time) * 1000
        )

        diagnostics = SchedulingDiagnostics(
             scheduling_report={"status": "success", "policy": self.policy.value, "type": "ExecutionPhaseGraph"},
             dependency_report={"roots": [], "leaves": [], "is_cyclic": False},
             critical_path_report={"path": [], "length": len(graph.phases)},
             execution_group_report={"groups_count": len(execution_groups)},
             parallelism_report={"estimated": estimated_parallelism},
             policy_report={"active_policy": self.policy.value},
             execution_ordering_report={"operations_count": len(ordered_operations)}
        )

        return ExecutionSchedule(
            ordered_operations=tuple(ordered_operations),
            dependency_levels={op: phase_idx for op, phase_idx in op_phase_map.items()},
            execution_groups=tuple(execution_groups),
            critical_path=tuple(),
            ready_queues=ready_queues,
            metadata={"policy": self.policy.value},
            diagnostics=diagnostics,
            statistics=stats
        )

    def _build_from_expert_graph(self, graph: Any, start_time: float) -> ExecutionSchedule:
        # 1. Routing Phase
        ordered_operations: List[str] = []
        ready_queues: Dict[int, List[str]] = {}
        execution_groups: List[ExecutionGroup] = []

        routing_op_id = graph.routing_graph.routing_node.id
        ordered_operations.append(routing_op_id)
        ready_queues[0] = [routing_op_id]

        execution_groups.append(ExecutionGroup(
             group_id=f"routing_group_{graph.group_id}",
             operations=[routing_op_id],
             dependency_level=0,
             parallelizable=False
        ))

        # 2. Experts Phase
        expert_op_ids = []
        for expert in graph.routing_graph.expert_graphs:
            for node in expert.expert_nodes:
                expert_op_ids.append(node.id)
                ordered_operations.append(node.id)

        if expert_op_ids:
            ready_queues[1] = expert_op_ids
            execution_groups.append(ExecutionGroup(
                 group_id=f"experts_group_{graph.group_id}",
                 operations=expert_op_ids,
                 dependency_level=1,
                 parallelizable=True
            ))

        stats = SchedulingStatistics(
            graph_depth=2 if expert_op_ids else 1,
            graph_width=len(expert_op_ids) if expert_op_ids else 1,
            critical_path_length=2 if expert_op_ids else 1,
            dependency_fan_in=1.0,
            dependency_fan_out=float(len(expert_op_ids)) if expert_op_ids else 1.0,
            parallel_groups=1 if expert_op_ids else 0,
            execution_levels=2 if expert_op_ids else 1,
            estimated_parallelism=len(ordered_operations) / 2 if expert_op_ids else 1.0,
            schedule_generation_time_ms=(time.time() - start_time) * 1000
        )

        diagnostics = SchedulingDiagnostics(
             scheduling_report={"status": "success", "policy": self.policy.value, "type": "ExpertExecutionGraph"},
             dependency_report={"roots": [routing_op_id], "leaves": expert_op_ids, "is_cyclic": False},
             critical_path_report={"path": [routing_op_id] + (expert_op_ids[:1] if expert_op_ids else []), "length": 2 if expert_op_ids else 1},
             execution_group_report={"groups_count": len(execution_groups)},
             parallelism_report={"estimated": stats.estimated_parallelism},
             policy_report={"active_policy": self.policy.value},
             execution_ordering_report={"operations_count": len(ordered_operations)}
        )

        return ExecutionSchedule(
            ordered_operations=ordered_operations,
            dependency_levels={op: 0 if op == routing_op_id else 1 for op in ordered_operations},
            execution_groups=execution_groups,
            critical_path=diagnostics.critical_path_report["path"],
            ready_queues=ready_queues,
            metadata={"policy": self.policy.value},
            diagnostics=diagnostics,
            statistics=stats
        )
