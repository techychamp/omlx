# Backpressure Report

## Concept
To prevent unbounded memory growth from slow consumers, all transports will utilize bounded queues (e.g., `maxsize=1000`).

## Mechanisms
1. **Bounded Buffering**: Each transport has a fixed-size buffer.
2. **Buffer Overflow Handling**: If a transport's queue fills up (consumer lag), the controller will attempt to push with a short timeout. If it times out, the transport is considered degraded and is automatically unsubscribed to prevent blocking the Runtime.
3. **Statistics**: Transports will expose metrics: `queue_size`, `events_dropped`, and `overflow_count`.
