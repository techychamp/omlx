import pytest
from omlx.runtime.scheduling.artifacts import (
    ExecutionPhaseGraph,
    ExecutionPhase,
    ExecutionPhaseType,
    ExecutionBarrier,
    SynchronizationPoint
)
from omlx.runtime.scheduling.scheduler import GraphScheduler
from omlx.runtime.scheduling.policies import SchedulingPolicy

def test_execution_phase_graph_scheduling():
    scheduler = GraphScheduler(policy=SchedulingPolicy.DEPENDENCY_DRIVEN)

    phases = [
        ExecutionPhase(
            name="device_prep",
            phase_type=ExecutionPhaseType.DEVICE_PREPARATION,
            operations=("init_device", "load_model")
        ),
        ExecutionPhase(
            name="compute",
            phase_type=ExecutionPhaseType.COMPUTE,
            operations=("matmul_1", "matmul_2")
        )
    ]

    graph = ExecutionPhaseGraph(phases=tuple(phases))
    schedule = scheduler.build_schedule(graph)

    assert len(schedule.execution_groups) == 2
    assert schedule.ordered_operations == ("init_device", "load_model", "matmul_1", "matmul_2")

    assert "init_device" in schedule.execution_groups[0].operations
    assert "matmul_1" in schedule.execution_groups[1].operations

if __name__ == "__main__":
    pytest.main([__file__])
