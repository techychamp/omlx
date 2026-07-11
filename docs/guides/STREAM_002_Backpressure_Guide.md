# STREAM-002: Backpressure Guide

## The Problem
Slow network connections or laggy UI consumers should never pause or crash the `Runtime` generation loop.

## Mechanism
1. **Bounded Queues**: Transports like `GeneratorTransport` use `queue.Queue(maxsize=...)` to limit memory growth.
2. **Timeouts**: Transports attempt to queue an event with a very small timeout (`0.01s`).
3. **Auto-Unsubscribe**: If the queue rejects the event, the transport raises a `BackpressureException`. The `StreamingController` catches this, automatically drops the slow subscriber, and emits a `WARNING` event.
