# Streaming Architecture Guide

## Overview
STREAM-001 introduces a compiler-native streaming framework designed to support incremental token generation without altering the existing execution architecture (`ExecutionEngine`).

## Core Components
- **`StreamingController`**: Manages the lifecycle of stream sessions and routes events to subscribers.
- **`StreamSession`**: An immutable snapshot container for streaming statistics, diagnostics, and token history.
- **`TokenEmitter`**: A consumer-friendly iterator that bridges the event-driven controller with a synchronous or asynchronous stream generator.
- **`StreamingToken`**: A backend-agnostic representation of a generated token.
- **`StreamingEvent`**: An immutable event emitted during the streaming lifecycle (e.g., `SessionStarted`, `TokenGenerated`, `Completed`).

## Design Principles
- **Observation, Not Execution**: The streaming framework observes the execution pipeline and does not assume responsibility for scheduling or the generation loop.
- **Thread Safety**: The system employs locking mechanisms (`threading.Lock`) and thread-safe data structures (`queue.Queue`) to guarantee safe concurrent operations and event dispatch.
- **Backend Agnostic**: The framework introduces token and event definitions that do not depend on MLX or specific tokenizers, ensuring ease of integration in BACKEND-005.

## Future Integration (BRIDGE-001)
When backend kernels are implemented, the `ExecutionEngine` or `BackendAdapter` will publish events (like `TokenGenerated`) directly to the `StreamingController`, mapping MLX output streams into the `TokenEmitter` seamlessly.
