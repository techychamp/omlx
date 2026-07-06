from typing import Any
import pytest
from omlx.planner.domains.moe.artifacts import (
    ExpertDescriptor,
    RoutingDescriptor,
    ExpertGroup,
    RoutingRequirement,
    RoutingStatistics,
    RoutingCompatibilityReport,
    RoutingValidationReport,
    MoEPlan
)
from omlx.planner.domains.moe.planner import MoEPlanner
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.api.v1.planning import PlanningClient, PlanningRequest

def test_moe_artifacts():
    expert1 = ExpertDescriptor(id="e1")
    expert2 = ExpertDescriptor(id="e2")
    group = ExpertGroup(id="g1", experts=(expert1, expert2))

    plan = MoEPlan(
        experts=(expert1, expert2),
        groups=(group,)
    )

    assert len(plan.experts) == 2
    assert plan.experts[0].id == "e1"
    assert len(plan.groups) == 1
    assert plan.groups[0].id == "g1"

def test_moe_planner():
    planner = MoEPlanner()
    descriptor = CapabilityDescriptor(execution_family=ExecutionFamily.AUTOREGRESSIVE)
    plan = planner.plan(descriptor)

    assert isinstance(plan, MoEPlan)
    assert len(plan.experts) == 0

def test_api_integration():
    client = PlanningClient()

    expert1 = ExpertDescriptor(id="e1")
    plan = MoEPlan(experts=(expert1,))

    bundle = PlanningBundle(
        execution_plan=ExecutionPlan(
            execution_family=ExecutionFamily.AUTOREGRESSIVE,
            execution_backend="cpu",
            execution_mode="sync",
            execution_topology="standalone",
            cache_strategy="none",
            scheduler_strategy="sequential",
            verification_stages=(),
            optimization_passes=()
        ),
        moe_plan=plan
    )

    diagnostics = client.get_moe_diagnostics(bundle)
    assert diagnostics["experts"] == 1
    assert diagnostics["groups"] == 0
    assert not diagnostics["has_routing"]

    comp, val = client.get_routing_reports(bundle)
    assert comp is None
    assert val is None

    stats = client.get_planning_statistics(bundle)
    assert stats is None
