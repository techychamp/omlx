from ...backend.descriptor import BackendDescriptor
from .reports import BackendCapabilityReport

class BackendCapabilityDiscovery:
    """Discovers capabilities of a backend without execution."""

    @staticmethod
    def discover(descriptor: BackendDescriptor) -> BackendCapabilityReport:
        """Discover backend capabilities from its descriptor."""
        return BackendCapabilityReport(
            supported_execution_families=descriptor.supported_execution_families,
            supported_optimization_phases=descriptor.supported_optimization_capabilities,
            supported_cache_layouts=descriptor.supported_cache_layouts,
            supported_synchronization_primitives=descriptor.supported_synchronization_primitives,
            supported_quantization_methods=descriptor.supported_quantization_formats,
            supported_model_families=descriptor.supported_execution_semantics,
            supports_graph_execution=bool(descriptor.supported_graph_features)
        )