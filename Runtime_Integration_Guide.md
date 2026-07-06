# Runtime Integration Guide
The Runtime no longer manages queue admission. It solely focuses on execution.
- Runtime creates a `RuntimeSession` either independently or by taking ownership of an admitted `QueueSession` via `RuntimeSession.from_queue_session()`.
- The `PlanningBundle` is attached to the `RuntimeSession` before the `ExecutionEngine` consumes it.
