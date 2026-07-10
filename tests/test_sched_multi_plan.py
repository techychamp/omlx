import pytest
from omlx.runtime.scheduling.artifacts import DependencyGraph, ExecutionPhase, DependencyBarrier, SynchronizationPoint
from omlx.runtime.scheduling.scheduler import GraphScheduler
from omlx.runtime.scheduling.policies import SchedulingPolicy
from omlx.planner.domains.bundle import PlanningBundle, MemoryPlan, CachePlan, VerificationPlan
from omlx.planner.plan import ExecutionPlan
from omlx.planner.device.artifacts import DevicePlan, ExecutionPlacement, ExecutionAffinity
from omlx.api.v1.planning import PlanningClient, PlanningRequest

def test_dependency_graph_from_bundle():
    client = PlanningClient()

    # Create a mock bundle with multiple plans
    bundle = PlanningBundle(
        execution_plan=ExecutionPlan(
        execution_family='autoregressive',
        execution_backend='mlx',
        execution_mode='standard',
        execution_topology='single',
        cache_strategy='paged',
        scheduler_strategy='continuous',
        verification_stages=tuple(),
        optimization_passes=tuple()
    ),
        device_plan=DevicePlan(placement=ExecutionPlacement(device_id='cpu', strategy='unified'), affinity=ExecutionAffinity(affinity_group='default', priority=1)),
        memory_plan=None,
        cache_plan=None,
        verification_plan=None
    )

    graph = client.extract_dependency_graph(bundle)

    assert isinstance(graph, DependencyGraph)
    assert len(graph.phases) == 2
    assert graph.phases[0].name == "device_placement"
    assert graph.phases[1].name == "compute"
    # assert graph.phases[2].name == "compute"

def test_scheduler_with_dependency_graph():
    client = PlanningClient()
    bundle = PlanningBundle(
        execution_plan=ExecutionPlan(
        execution_family='autoregressive',
        execution_backend='mlx',
        execution_mode='standard',
        execution_topology='single',
        cache_strategy='paged',
        scheduler_strategy='continuous',
        verification_stages=tuple(),
        optimization_passes=tuple()
    ),
        device_plan=DevicePlan(placement=ExecutionPlacement(device_id='cpu', strategy='unified'), affinity=ExecutionAffinity(affinity_group='default', priority=1)),
        memory_plan=None,
        cache_plan=None,
        verification_plan=None
    )
    graph = client.extract_dependency_graph(bundle)

    scheduler = GraphScheduler(policy=SchedulingPolicy.DEPENDENCY_DRIVEN)
    schedule = scheduler.build_schedule(graph)

    assert schedule is not None
    assert len(schedule.execution_groups) == 2
    assert schedule.diagnostics.scheduling_report["type"] == "DependencyGraph"
