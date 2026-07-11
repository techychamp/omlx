# Profiling Documentation

The `Profiler` class measures resource consumption for single compiler operations.

## Usage
```python
from omlx.compiler_perf.profiler import Profiler

result = Profiler.profile("stage_name", my_function)
print(result.peak_memory_bytes)
print(result.cpu_time_ms)
```
Metrics tracked: Wall Time, CPU Time, Peak Memory, Memory Diff.
