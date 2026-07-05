import time
import tracemalloc
from dataclasses import dataclass
from typing import Callable, Any, Dict, Optional

@dataclass
class ProfileResult:
    name: str
    wall_time_ms: float
    cpu_time_ms: float
    peak_memory_bytes: int
    memory_diff_bytes: int

class Profiler:
    """Measures performance and memory characteristics of compiler stages."""

    @staticmethod
    def profile(name: str, func: Callable, *args, **kwargs) -> ProfileResult:
        """Profiles a single execution of a function."""
        # Memory profiling
        tracemalloc.start()
        start_mem, _ = tracemalloc.get_traced_memory()

        # Time profiling
        start_wall = time.perf_counter()
        start_cpu = time.process_time()

        # Execute
        _ = func(*args, **kwargs)

        # End time
        end_cpu = time.process_time()
        end_wall = time.perf_counter()

        # End memory
        end_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return ProfileResult(
            name=name,
            wall_time_ms=(end_wall - start_wall) * 1000.0,
            cpu_time_ms=(end_cpu - start_cpu) * 1000.0,
            peak_memory_bytes=peak_mem,
            memory_diff_bytes=end_mem - start_mem
        )

    @staticmethod
    def format_bytes(b: int) -> str:
        """Format bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if b < 1024.0:
                return f"{b:.2f} {unit}"
            b /= 1024.0
        return f"{b:.2f} TB"
