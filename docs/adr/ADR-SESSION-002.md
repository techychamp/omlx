# Architecture Decision Record: SESSION-002

**Context**: ExecutionEngine historically consumed `ExecutionContext` directly.
**Decision**: Reposition `RuntimeSession` as the fundamental container for all engine and compiler coordination.
**Status**: Accepted and implemented.