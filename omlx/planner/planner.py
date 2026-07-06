import time
from typing import Optional, TYPE_CHECKING, Any
from types import MappingProxyType
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.planner.plan import ExecutionPlan
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.compiler.planner import CompilerPlanner

from omlx.planner.passes import PassRegistry
from omlx.planner.validation import validate_plan
from omlx.planner.compiler.cache.utils import compute_cache_key
if TYPE_CHECKING:
    from omlx.planner.compiler.dependency_tracker import DependencyTracker
if TYPE_CHECKING:
    from omlx.planner.compiler.cache.manager import CompilerCacheManager

class ExecutionPlanner:
    """
    Transforms a CapabilityDescriptor into an immutable ExecutionPlan.
    """
    def __init__(self, pass_registry: PassRegistry | None = None, capability_resolver=None, feature_flags=None, runtime_context=None, registries=None, cache_manager: Optional['CompilerCacheManager'] = None, dependency_tracker: Optional['DependencyTracker'] = None):
        self._pass_registry = pass_registry or PassRegistry()
        self._capability_resolver = capability_resolver
        self._feature_flags = feature_flags
        self._runtime_context = runtime_context
        self._registries = registries
        self.cache_manager = cache_manager
        self.dependency_tracker = dependency_tracker

    def plan(self, descriptor: CapabilityDescriptor, strategy_intent: Any = None) -> PlanningBundle:
        """Creates an ExecutionPlan from a CapabilityDescriptor."""

        cache_key = compute_cache_key("plan", descriptor)
        if self.cache_manager:
            cached = self.cache_manager.get(cache_key)
            if cached:
                return cached.value

        start_time = time.time()

        # Base Plan Construction
        plan_dict = {
            "execution_family": descriptor.execution_family,
            "execution_backend": self._select_backend(descriptor),
            "execution_mode": self._select_mode(descriptor),
            "execution_topology": "single_node",
            "cache_strategy": descriptor.cache_layout,
            "scheduler_strategy": "continuous_batching" if descriptor.supports_streaming else "static_batching",
            "verification_stages": ("model_load",) if descriptor.supports_verification else tuple(),
            "optimization_passes": [],
            "execution_hints": dict(descriptor.execution_hints),
            "hardware_requirements": tuple(descriptor.hardware_requirements),
            "planner_metadata": {}
        }

        # Apply Optimization Passes
        for p in self._pass_registry.get_passes():
            p.apply(plan_dict, descriptor)
            plan_dict["optimization_passes"].append(p.name)

        plan_dict["optimization_passes"] = tuple(plan_dict["optimization_passes"])

        plan_dict["planner_metadata"]["planning_time_ms"] = (time.time() - start_time) * 1000

        # Construct immutable plan
        plan_dict["execution_hints"] = MappingProxyType(plan_dict["execution_hints"])
        plan_dict["planner_metadata"] = MappingProxyType(plan_dict["planner_metadata"])
        plan = ExecutionPlan(**plan_dict)

        # Validation
        # Inject cache key into metadata
        metadata = dict(plan.planner_metadata)
        metadata["cache_key"] = cache_key
        object.__setattr__(plan, "planner_metadata", metadata)

        validate_plan(plan)

        if self.cache_manager:
            self.cache_manager.put(cache_key, plan, size_bytes=2048, version="v1")
            if getattr(self, 'dependency_tracker', None):
                upstream_key = descriptor._diagnostics.get("cache_key") if descriptor._diagnostics else None
                if upstream_key:
                    self.dependency_tracker.record_dependency(upstream_key, cache_key)


        compiler_planner = CompilerPlanner()
        return compiler_planner.compose_bundle(descriptor, plan, strategy_intent=strategy_intent)


    def _select_backend(self, descriptor: CapabilityDescriptor) -> str:
        if descriptor.execution_family == ExecutionFamily.AUTOREGRESSIVE:
            if descriptor.supports_speculative:
                return "speculative"
            return "autoregressive"
        elif descriptor.execution_family == ExecutionFamily.DIFFUSION:
            return "diffusion"
        elif descriptor.execution_family == ExecutionFamily.EMBEDDING:
            return "embedding"
        return "unknown"

    def _select_mode(self, descriptor: CapabilityDescriptor) -> str:
        if descriptor.supports_streaming:
             return "streaming"
        return "standard"
