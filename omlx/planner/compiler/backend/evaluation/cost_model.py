from ...backend.descriptor import BackendDescriptor
from .benchmark import BackendBenchmarkProfile
from .reports import BackendCostReport

class BackendCostModel:
    """Estimates the execution cost for a backend without active execution."""

    @staticmethod
    def estimate_cost(
        descriptor: BackendDescriptor,
        benchmark: BackendBenchmarkProfile | None = None
    ) -> BackendCostReport:
        """Estimate execution cost for the given backend."""
        # Baseline estimations derived from descriptor properties
        has_compiled_graph = bool(descriptor.supported_graph_features)
        is_hardware_accelerated = any("gpu" in hc.lower() or "metal" in hc.lower() for hc in descriptor.hardware_capabilities)

        if benchmark:
            latency = benchmark.reference_latency_ms
            memory = benchmark.reference_memory_usage_mb
            startup = benchmark.reference_startup_time_ms
            throughput = benchmark.reference_throughput_tokens_per_sec
        else:
            latency = descriptor.estimated_latency if descriptor.estimated_latency > 0 else (10.0 if is_hardware_accelerated else 50.0)

            # Use estimated_memory_usage, fallback to peak_memory_estimate, then default
            if descriptor.estimated_memory_usage > 0:
                memory = descriptor.estimated_memory_usage
            elif descriptor.peak_memory_estimate > 0:
                memory = descriptor.peak_memory_estimate
            else:
                memory = 1024.0

            startup = 500.0 if has_compiled_graph else 100.0
            throughput = descriptor.estimated_throughput if descriptor.estimated_throughput > 0 else (100.0 if is_hardware_accelerated else 20.0)

        return BackendCostReport(
            estimated_latency_ms=latency,
            estimated_peak_memory_mb=memory,
            estimated_startup_time_ms=startup,
            cache_efficiency_score=descriptor.cache_efficiency if descriptor.cache_efficiency > 0 else (0.9 if has_compiled_graph else 0.5),
            graph_complexity_score=descriptor.graph_execution_efficiency if descriptor.graph_execution_efficiency > 0 else (0.8 if has_compiled_graph else 0.2),
            estimated_throughput_tokens_per_sec=throughput,
            hardware_utilization_score=0.85 if is_hardware_accelerated else 0.3
        )