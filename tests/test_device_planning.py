import pytest
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.planner.device import (
    DevicePlanner,
    DevicePlan,
    ExecutionPlacement,
    ExecutionAffinity,
    DeviceRequirement
)
from omlx.planner.plan import ExecutionPlan
from omlx.planner.bundle import PlanningBundle

def test_device_plan_creation():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        hardware_requirements=("apple_silicon",)
    )

    planner = DevicePlanner()
    device_plan = planner.plan(descriptor)

    assert isinstance(device_plan, DevicePlan)
    assert device_plan.requirements.required_device_type == "apple_silicon"
    assert device_plan.placement.strategy == "unified_memory"
    assert device_plan.affinity.priority == 100

def test_planning_bundle_composition():
    execution_plan = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="standard",
        execution_topology="single_node",
        cache_strategy="paged",
        scheduler_strategy="continuous",
        verification_stages=tuple(),
        optimization_passes=tuple()
    )

    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        hardware_requirements=("apple_silicon",)
    )
    device_planner = DevicePlanner()
    device_plan = device_planner.plan(descriptor)

    bundle = PlanningBundle(
        execution_plan=execution_plan,
        device_plan=device_plan
    )

    assert bundle.execution_plan == execution_plan
    assert bundle.device_plan == device_plan
    assert bundle.cache_plan is None
