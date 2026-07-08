# Queue Lifecycle Guide
1. **Incoming Request**: Arrives at the system.
2. **Admission**: `QueueAdmissionController` creates an immutable `QueueEntry`.
3. **QueueSession**: `QueueManager` wraps the entry in a `QueueSession` with status 'queued'.
4. **Ordering**: Request waits in the queue based on prioritization.
5. **Dequeue**: Request is dequeued, and the `QueueSession` status becomes 'ready_for_execution'.
6. **Handoff**: The `QueueSession` is passed to the Runtime.
7. **RuntimeSession**: Runtime converts it to a `RuntimeSession` to manage actual execution.
