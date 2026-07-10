import pytest
from omlx.runtime.scheduling.artifacts import DependencyGraph, ExecutionPhase, DependencyBarrier, SynchronizationPoint
from omlx.runtime.scheduling.scheduler import GraphScheduler
from omlx.runtime.scheduling.policies import SchedulingPolicy
from omlx.planner.domains.bundle import PlanningBundle, MemoryPlan, CachePlan, VerificationPlan

def extract_dependency_graph(bundle: PlanningBundle) -> DependencyGraph:
    # Build phases based on plans
    phases = []

    # 1. Device phase (optional)
    if bundle.device_plan:
         phases.append(ExecutionPhase(
             name="device_placement",
             operations=["allocate_devices", "map_topology"],
             barriers=[DependencyBarrier(name="device_ready")]
         ))

    # 2. Memory phase (optional)
    if bundle.memory_plan:
         phases.append(ExecutionPhase(
             name="memory_allocation",
             operations=["allocate_tensors", "setup_kv_cache"],
             barriers=[DependencyBarrier(name="memory_ready")]
         ))

    # 3. Execution phase
    if bundle.execution_plan:
         ops = ["execute_model"]
         phases.append(ExecutionPhase(
             name="compute",
             operations=ops,
             sync_points=[SynchronizationPoint(name="compute_done")]
         ))

    return DependencyGraph(
        operations={op: {"type": "abstract"} for p in phases for op in p.operations},
        phases=phases,
        metadata={"source": "PlanningBundle"}
    )


def test_dependency_graph_from_bundle():
    # Create a mock bundle with multiple plans
    bundle = PlanningBundle(
        execution_plan="dummy_plan",
        device_plan="dummy_device",
        memory_plan=MemoryPlan(),
        cache_plan=None,
        verification_plan=None
    )

    graph = extract_dependency_graph(bundle)

    assert isinstance(graph, DependencyGraph)
    assert len(graph.phases) == 3
    assert graph.phases[0].name == "device_placement"
    assert graph.phases[1].name == "memory_allocation"
    assert graph.phases[2].name == "compute"

def test_scheduler_with_dependency_graph():
    bundle = PlanningBundle(
        execution_plan="dummy_plan",
        device_plan="dummy_device",
        memory_plan=MemoryPlan(),
        cache_plan=None,
        verification_plan=None
    )
    graph = extract_dependency_graph(bundle)

    scheduler = GraphScheduler(policy=SchedulingPolicy.DEPENDENCY_DRIVEN)
    schedule = scheduler.build_schedule(graph)

    assert schedule is not None
    assert len(schedule.execution_groups) == 3
    assert schedule.diagnostics.scheduling_report["type"] == "DependencyGraph"
