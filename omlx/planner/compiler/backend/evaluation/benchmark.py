from dataclasses import dataclass, field

@dataclass(frozen=True)
class BackendBenchmarkProfile:
    """Benchmark metadata for a backend."""
    reference_latency_ms: float
    reference_throughput_tokens_per_sec: float
    reference_memory_usage_mb: float
    reference_startup_time_ms: float
    reference_optimization_score: float
    reference_hardware_classes: tuple[str, ...] = field(default_factory=tuple)
