# STREAM-002: Streaming Runtime Architecture Guide

## Core Ownership
The compiler-native Runtime strictly owns the entire generation lifecycle.
- **Runtime** manages the model decode loop, execution scheduling, and cancellation checks.
- **Streaming subsystem** acts strictly as an asynchronous observer and dispatcher.
- **ExecutionEngine** and **BackendAdapter** remain completely unaware of streaming.

## Components
1. **StreamingController**: The central thread-safe event bus that registers `StreamSession` instances and routes events to subscribers.
2. **StreamSession**: Stores historical events and basic statistics for an active generation task.
3. **StreamingTransport**: An abstraction (`CallbackTransport`, `GeneratorTransport`) that consumers implement to receive events asynchronously via bounded queues.

## Lifecycle
1. `Runtime.generate()` creates a session via `StreamingController`.
2. The runtime loop emits `StreamingEvent`s (e.g., `TOKEN_GENERATED`).
3. The controller passes these events to all registered transports.
4. Slow consumers encountering backpressure (full queues) are automatically unsubscribed.
5. The runtime completes or cancels the generation loop, finalizing the session state.
