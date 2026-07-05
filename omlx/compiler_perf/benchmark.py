import time
from typing import Callable, Any, Dict

class BenchmarkResult:
    def __init__(self, name: str):
        self.name = name
        self.iterations = 0
        self.total_time_ms = 0.0
        self.min_time_ms = float('inf')
        self.max_time_ms = 0.0

    def record(self, time_ms: float):
        self.iterations += 1
        self.total_time_ms += time_ms
        self.min_time_ms = min(self.min_time_ms, time_ms)
        self.max_time_ms = max(self.max_time_ms, time_ms)

    @property
    def avg_time_ms(self) -> float:
        if self.iterations == 0:
            return 0.0
        return self.total_time_ms / self.iterations

    def to_dict(self) -> Dict[str, float]:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time_ms": self.total_time_ms,
            "min_time_ms": self.min_time_ms if self.iterations > 0 else 0.0,
            "max_time_ms": self.max_time_ms,
            "avg_time_ms": self.avg_time_ms
        }

def benchmark_stage(name: str, func: Callable, iterations: int = 1, *args, **kwargs) -> BenchmarkResult:
    """Benchmarks a specific compiler stage execution."""
    result = BenchmarkResult(name)

    for _ in range(iterations):
        start = time.perf_counter()
        _ = func(*args, **kwargs)
        end = time.perf_counter()

        result.record((end - start) * 1000.0)

    return result

class CompilerBenchmarkSuite:
    """Helper to benchmark multiple stages of the compiler pipeline."""
    def __init__(self):
        self.results: Dict[str, BenchmarkResult] = {}

    def add_benchmark(self, name: str, func: Callable, iterations: int = 10, *args, **kwargs):
        self.results[name] = benchmark_stage(name, func, iterations, *args, **kwargs)

    def run_full_pipeline(self,
                          resolve_func: Callable,
                          plan_func: Callable,
                          logical_ir_func: Callable,
                          physical_ir_func: Callable,
                          translation_func: Callable,
                          iterations: int = 10):
        """Runs benchmarks for all stages (mock functions provided by the caller)."""
        # Inference should not be benchmarked here, only compiler stages
        self.add_benchmark("capability_resolution", resolve_func, iterations)
        self.add_benchmark("execution_planning", plan_func, iterations)
        self.add_benchmark("logical_ir_generation", logical_ir_func, iterations)
        self.add_benchmark("physical_ir_lowering", physical_ir_func, iterations)
        self.add_benchmark("backend_translation", translation_func, iterations)

    def get_report(self) -> Dict[str, Dict]:
        return {name: result.to_dict() for name, result in self.results.items()}
