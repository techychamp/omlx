import time
from typing import Any
from types import MappingProxyType
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.planner.plan import ExecutionPlan
from omlx.planner.passes import PassRegistry
from omlx.planner.validation import validate_plan

class ExecutionPlanner:
    """
    Transforms a CapabilityDescriptor into an immutable ExecutionPlan.
    """
    def __init__(self, pass_registry: PassRegistry | None = None, capability_resolver=None, feature_flags=None, runtime_context=None, registries=None):
        self._pass_registry = pass_registry or PassRegistry()
        self._capability_resolver = capability_resolver
        self._feature_flags = feature_flags
        self._runtime_context = runtime_context
        self._registries = registries

    def plan(self, descriptor: CapabilityDescriptor) -> ExecutionPlan:
        """Creates an ExecutionPlan from a CapabilityDescriptor."""

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
        validate_plan(plan)

        return plan

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
