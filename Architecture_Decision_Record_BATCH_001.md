# ADR: Compiler-Native Batch Execution

**Decision**: Introduce compiler-native batch execution as an independent Planning Domain and Generation Strategy, preserving existing Runtime, Scheduler, and Backend architectures.
**Rationale**: Keeps batching policy isolated, deterministic, and immutable.
