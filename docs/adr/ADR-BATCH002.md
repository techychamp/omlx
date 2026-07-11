# Architecture Decision Record: BATCH-002

## Decision
All batch realization (grouping, synchronization, graph generation) must happen strictly within the Compiler.

## Justification
Keeping the Runtime and Execution Engine free of batching logic ensures they remain deterministic, predictable, and simple. Adapting batching logic as a runtime queue-merging exercise creates non-deterministic execution behavior and hides latency bottlenecks.
