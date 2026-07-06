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
    plan = planner.plan(descriptor).execution_plan

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
    plan = planner.plan(descriptor).execution_plan

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
    plan = planner.plan(descriptor).execution_plan

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
    plan = planner.plan(descriptor).execution_plan

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

    plan = planner.plan(descriptor).execution_plan

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
    plan = planner.plan(descriptor).execution_plan

    with pytest.raises(Exception): # FrozenInstanceError
        plan.execution_backend = "something_else"

def test_fusion_plan_integration():
    from omlx.framework.graph.artifacts import GraphAnalysisReport, GraphDescriptor
    from omlx.runtime.scheduling.artifacts import DependencyGraph
    from types import MappingProxyType

    class StrategyIntentMock:
        def __init__(self):
            self.graph_descriptor = GraphDescriptor(id="mock")
            self.dependency_graph = DependencyGraph(operations={"node_1": {}, "node_2": {}})
            self.analysis_report = GraphAnalysisReport(node_properties=MappingProxyType({
                "node_1": {"fusion_candidate": True, "fusion_target": "node_2", "fusion_type": "QKV"}
            }))

    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        supported_modalities=("text",),
        attention_types=(AttentionType.CAUSAL,),
        cache_layout=CacheLayoutType.PAGED,
        supports_streaming=True,
        supports_speculative=False
    )

    planner = ExecutionPlanner()
    bundle = planner.plan(descriptor, strategy_intent=StrategyIntentMock())

    assert bundle.fusion_plan is not None
    assert len(bundle.fusion_plan.groups) == 1
    assert bundle.fusion_plan.statistics.nodes_fused == 2
