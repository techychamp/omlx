import pytest
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily, CacheLayoutType, AttentionType
from omlx.planner.planner import ExecutionPlanner
from omlx.planner.plan import ExecutionPlan
from omlx.planner.passes import PlanningPass, PassRegistry
from omlx.planner.validation import PlannerValidationError

def test_plan_autoregressive():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        supported_modalities=("text",),
        attention_types=(AttentionType.CAUSAL,),
        cache_layout=CacheLayoutType.PAGED,
        supports_streaming=True,
        supports_speculative=False
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor)

    assert plan.execution_family == ExecutionFamily.AUTOREGRESSIVE
    assert plan.execution_backend == "autoregressive"
    assert plan.execution_mode == "streaming"
    assert plan.cache_strategy == CacheLayoutType.PAGED
    assert plan.scheduler_strategy == "continuous_batching"

def test_plan_speculative():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        supported_modalities=("text",),
        attention_types=(AttentionType.CAUSAL,),
        cache_layout=CacheLayoutType.PAGED,
        supports_streaming=True,
        supports_speculative=True
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor)

    assert plan.execution_family == ExecutionFamily.AUTOREGRESSIVE
    assert plan.execution_backend == "speculative"

def test_plan_diffusion():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.DIFFUSION,
        supported_modalities=("text", "vision"),
        attention_types=(AttentionType.DIFFUSION,),
        cache_layout=CacheLayoutType.NONE,
        supports_streaming=False,
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor)

    assert plan.execution_family == ExecutionFamily.DIFFUSION
    assert plan.execution_backend == "diffusion"
    assert plan.execution_mode == "standard"
    assert plan.scheduler_strategy == "static_batching"

def test_plan_embedding():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.EMBEDDING,
        supported_modalities=("text",),
        attention_types=(AttentionType.BIDIRECTIONAL,),
        cache_layout=CacheLayoutType.NONE,
        supports_streaming=False,
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor)

    assert plan.execution_family == ExecutionFamily.EMBEDDING
    assert plan.execution_backend == "embedding"
    assert plan.execution_mode == "standard"

def test_planning_pass():
    class TestPass:
        @property
        def name(self):
            return "test_pass"

        def apply(self, plan: dict, descriptor: CapabilityDescriptor) -> None:
            plan["execution_hints"]["test_pass_applied"] = True

    registry = PassRegistry()
    registry.register(TestPass())

    planner = ExecutionPlanner(pass_registry=registry)
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE
    )

    plan = planner.plan(descriptor)

    assert "test_pass" in plan.optimization_passes
    assert plan.execution_hints.get("test_pass_applied") is True

def test_validation_failure():
    class BadPass:
        @property
        def name(self):
            return "bad_pass"

        def apply(self, plan: dict, descriptor: CapabilityDescriptor) -> None:
            plan["execution_backend"] = ""

    registry = PassRegistry()
    registry.register(BadPass())

    planner = ExecutionPlanner(pass_registry=registry)
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE
    )

    with pytest.raises(PlannerValidationError) as exc_info:
        planner.plan(descriptor)

    assert "Execution backend must be specified" in exc_info.value.errors

def test_immutable_plan():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor)

    with pytest.raises(Exception): # FrozenInstanceError
        plan.execution_backend = "something_else"
