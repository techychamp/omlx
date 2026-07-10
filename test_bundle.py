import pytest
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.plan import ExecutionPlan
from omlx.planner.domains.batch import BatchPlanner
from omlx.capabilities.descriptor import ExecutionFamily, CacheLayoutType

def test_bundle_batch_plan():
    planner = BatchPlanner()
    batch_plan = planner.plan(["req1", "req2"])

    execution_plan = ExecutionPlan(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        execution_backend="mlx",
        execution_mode="eager",
        execution_topology="single_device",
        cache_strategy=CacheLayoutType.PAGED,
        scheduler_strategy="dependency",
        verification_stages=("schema_validation",),
        optimization_passes=("fusion",)
    )

    bundle = PlanningBundle(
        execution_plan=execution_plan,
        batch_plan=batch_plan
    )

    assert bundle.batch_plan is not None
    assert bundle.batch_plan.batch_descriptor.batch_id == "batch_0"
    assert bundle.batch_plan.batch_descriptor.request_ids == ["req1", "req2"]
