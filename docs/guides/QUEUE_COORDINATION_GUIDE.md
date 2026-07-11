# Queue Coordination Guide

The OMLX Queue Coordination architecture implements a compiler-native queueing layer designed to act as the canonical execution coordination layer while preserving explicit subsystem ownership.

## Subsystem Ownership Principles

- **Queue owns**: Request admission, queue ordering, execution readiness, and queue diagnostics.
- **Runtime owns**: QueueManager initialization and lifecycle orchestration (e.g., publishing `RuntimeLifecycleEvent.QUEUE_ADMITTED`).
- **Scheduler owns**: Execution synchronization and dependency ordering. **Scheduler never performs queue management.**
- **Compiler owns**: Execution graph generation and planning.

## Flow
1. A request enters via the Runtime.
2. The Runtime explicitly delegates it to the `QueueManager` using `enqueue_request()`.
3. A `QueueSession` is created representing the pre-execution lifecycle.
4. When dequeued, the queue transfers ownership to a `RuntimeSession`.
5. The Scheduler executes the `RuntimeSession`.
