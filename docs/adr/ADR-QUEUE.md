# Architecture Decision Record: Compiler-Native Queue Coordination

## Context
With the expansion of speculative execution, advanced memory planning, and batching features, OMLX requires a unified coordination layer that bridges the incoming API layer and the backend Scheduler without conflating their responsibilities.

## Decision
We introduce a strictly scoped `QueueManager` layer.
The Queue manages *readiness* (admission and priority), while the Scheduler manages *execution* (dependency and synchronization).

## Consequences
- The Runtime requires a `QueueManager` instance.
- Tooling and API layers only interact with immutable queue diagnostic artifacts.
- Future batching logic (e.g., Continuous Batching) can interface directly with `QueueManager` without mutating backend graph execution.
