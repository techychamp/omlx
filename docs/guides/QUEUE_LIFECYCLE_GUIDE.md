# Queue Lifecycle Guide

The lifecycle of an admitted request inside the Queue framework is strictly delineated from execution.

1. **Admission**: `QueueAdmissionController` validates and accepts the request, creating an immutable `QueueEntry`.
2. **Queuing**: `QueueManager` wraps the entry in a `QueueSession` with status "queued".
3. **Dequeuing**: `QueueManager` pops the session, updating its state to "ready_for_execution".
4. **Handoff**: The Queue stops tracking active execution once a `RuntimeSession` takes over.
5. **Removal**: Upon execution completion or cancellation, the session is cleared from the QueueManager via `remove_session()`.
