from typing import Dict
from omlx.compiler_perf.cache import (
    CompilerCache, CapabilityCache, PlanCache,
    LogicalIRCache, PhysicalIRCache, BackendGraphCache
)
from omlx.compiler_perf.diagnostics import CacheDiagnostics

class CacheManager:
    """Orchestrates all compiler cache layers and aggregates diagnostics."""
    def __init__(self, max_sizes: Dict[str, int] = None):
        self.diagnostics = CacheDiagnostics()

        sizes = max_sizes or {}

        self.capability = CapabilityCache(
            max_size=sizes.get("capability", 1000),
            diagnostics=self.diagnostics
        )
        self.plan = PlanCache(
            max_size=sizes.get("plan", 1000),
            diagnostics=self.diagnostics
        )
        self.logical_ir = LogicalIRCache(
            max_size=sizes.get("logical_ir", 500),
            diagnostics=self.diagnostics
        )
        self.physical_ir = PhysicalIRCache(
            max_size=sizes.get("physical_ir", 500),
            diagnostics=self.diagnostics
        )
        self.backend_graph = BackendGraphCache(
            max_size=sizes.get("backend_graph", 100),
            diagnostics=self.diagnostics
        )

        self.caches = {
            "capability": self.capability,
            "plan": self.plan,
            "logical_ir": self.logical_ir,
            "physical_ir": self.physical_ir,
            "backend_graph": self.backend_graph
        }

    def clear_all(self) -> None:
        """Clears all caches."""
        for cache in self.caches.values():
            cache.clear()

    def get_diagnostics(self) -> Dict:
        """Returns the aggregated diagnostics for all layers."""
        return self.diagnostics.get_snapshot()
