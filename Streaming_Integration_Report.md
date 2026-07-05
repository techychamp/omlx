# Streaming Integration Report

- **Integration Point**: `ExecutionEngine` -> `StreamingController`.
- **Mechanism**: The execution engine or backend adapters will publish events to a `StreamingController`.
- **No Execution Ownership**: Streaming components (like `StreamSession`, `StreamingController`) will NOT own the generation loop or schedule tasks. They will merely act as sinks for events and sources for the client.
- **Thread Safety**: We will use thread-safe queues or asynchronous primitives to decouple event publication from client consumption.
