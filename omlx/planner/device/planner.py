import time
from typing import Optional, TYPE_CHECKING
from types import MappingProxyType

from omlx.capabilities.descriptor import CapabilityDescriptor
from omlx.planner.device.artifacts import (
    DevicePlan, ExecutionPlacement, ExecutionAffinity,
)
from omlx.planner.compiler.cache.utils import compute_cache_key

if TYPE_CHECKING:
    from omlx.planner.compiler.dependency_tracker import DependencyTracker
    from omlx.planner.compiler.cache.manager import CompilerCacheManager

class DevicePlanner:
    """
    Transforms a CapabilityDescriptor into an immutable DevicePlan.
    """
    def __init__(
        self,
        cache_manager: Optional['CompilerCacheManager'] = None,
        dependency_tracker: Optional['DependencyTracker'] = None
    ):
        self.cache_manager = cache_manager
        self.dependency_tracker = dependency_tracker

    def plan(self, descriptor: CapabilityDescriptor) -> DevicePlan:
        cache_key = compute_cache_key("device_plan", descriptor)
        if self.cache_manager:
            cached = self.cache_manager.get(cache_key)
            if cached:
                return cached.value

        start_time = time.time()

        # Simple logic for finding Apple Silicon or generic GPU constraints for now
        is_apple_silicon = "apple_silicon" in getattr(descriptor, 'hardware_requirements', []) or getattr(descriptor, 'is_mlx_compatible', False)

        # Handle potential missing memory requirements in descriptor
        min_memory = 0
        if hasattr(descriptor, 'memory_requirements') and isinstance(descriptor.memory_requirements, dict):
            min_memory = descriptor.memory_requirements.get('minimum_bytes', 0)

        hw_reqs = tuple(getattr(descriptor, 'hardware_requirements', []))

        if is_apple_silicon:
            reqs = dict(
                required_device_type="apple_silicon",
                minimum_memory=min_memory,
                required_capabilities=hw_reqs
            )
            placement = ExecutionPlacement(device_id="default_apple_silicon", strategy="unified_memory")
            affinity = ExecutionAffinity(affinity_group="apple_silicon_group", priority=100)
        else:
            reqs = dict(
                required_device_type="generic_gpu",
                minimum_memory=min_memory,
                required_capabilities=hw_reqs
            )
            placement = ExecutionPlacement(device_id="default_gpu", strategy="vram")
            affinity = ExecutionAffinity(affinity_group="gpu_group", priority=50)

        metadata = MappingProxyType({
            "planning_time_ms": (time.time() - start_time) * 1000,
            "cache_key": cache_key
        })

        plan = DevicePlan(
            placement=placement,
            affinity=affinity,

            planner_metadata=metadata
        )

        if self.cache_manager:
            self.cache_manager.put(cache_key, plan, size_bytes=1024, version="v1")
            if getattr(self, 'dependency_tracker', None):
                upstream_key = descriptor._diagnostics.get("cache_key") if getattr(descriptor, '_diagnostics', None) else None
                if upstream_key:
                    self.dependency_tracker.record_dependency(upstream_key, cache_key)

        return plan
