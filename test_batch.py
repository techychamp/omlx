import pytest
from omlx.planner.domains.batch import BatchPlanner
from omlx.planner.bundle import PlanningBundle
from omlx.planner.plan import ExecutionPlan
from omlx.runtime.generation.batch import BatchGenerationStrategy

def test_batch_planner():
    planner = BatchPlanner()
    plan = planner.plan(["req1", "req2"])

    assert plan.batch_descriptor.batch_id == "batch_0"
    assert plan.batch_descriptor.request_ids == ["req1", "req2"]
    assert plan.requirements.max_batch_size == 32
    assert plan.compatibility_report.is_compatible is True

def test_planning_bundle_with_batch():
    # We will modify bundle to accept batch_plan
    pass

def test_batch_generation_strategy():
    strategy = BatchGenerationStrategy()
    assert strategy.strategy_intent == "batch"
    assert strategy.get_cache_policy()["policy"] == "batch_optimized"
    assert strategy.generate(None, None) == "batch_execution"
