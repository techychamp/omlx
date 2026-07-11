# Runtime Integration Guide

Integrating the Queue with Runtime is designed to be fully unobtrusive to existing execution paths.

- **Instantiation**: The `RuntimeBuilder` instantiates a `QueueManager` and injects it into the `RuntimeContext`.
- **Events**: The `Runtime` instance hooks queue methods (`enqueue_request`, `dequeue_request`) and publishes `QUEUE_ADMITTED` / `QUEUE_DEQUEUED` events to the EventBus.
- **API Visibility**: The public API (`RuntimeService`) explicitly wraps `QueueAPI` to provide read-only views for `get_queue_statistics()` and `get_queue_diagnostics()`.
