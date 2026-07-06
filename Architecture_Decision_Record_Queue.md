# Architecture Decision Record: Queue
**Context**: OMLX requires a unified way to handle incoming requests before they hit the execution runtime to support future batching and distributed execution.
**Decision**: Implement a separate Compiler-Native Queue Framework (QUEUE-001) that strictly manages admission and pre-execution lifecycle without performing actual execution.
**Consequences**: Clean separation of concerns. Runtime focuses only on execution. Paves the way for BATCH-002 (Continuous Batching).
