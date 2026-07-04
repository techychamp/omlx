# Cost Model Architecture Report
The Backend Cost Models provide immutable representations of theoretical execution costs without performing active benchmarking.
Models included:
- `MemoryCostModel`: Base and per-token memory usage estimates.
- `LatencyCostModel`: Base latency and time-to-first-token.
- `SynchronizationCostModel`: Barrier and stream synchronization costs.
- `TransferCostModel`: Data transfer bandwidth capabilities.
- `CompilationCostModel`: Estimated compile time and cache efficiency.
- `ExecutionCostModel`: Compute efficiency metrics.
- `CacheCostModel`: Cache operation costs.
- `RoutingCostModel`: Expert routing overheads.
