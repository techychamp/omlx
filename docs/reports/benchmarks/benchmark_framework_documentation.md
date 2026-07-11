# Benchmark Framework Documentation

The `CompilerBenchmarkSuite` provides a harness for evaluating compiler stage latencies over multiple iterations without executing inference.

## Usage
```python
from omlx.compiler_perf.benchmark import CompilerBenchmarkSuite

suite = CompilerBenchmarkSuite()
suite.add_benchmark("stage_name", my_function, iterations=10)
report = suite.get_report()
```
Metrics tracked include: Total Time, Min Time, Max Time, Average Time (all in milliseconds).
