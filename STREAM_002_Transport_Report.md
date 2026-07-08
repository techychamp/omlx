# Transport Report

## Abstraction
A new `BaseTransport` interface will be introduced with methods:
- `on_event(event: StreamingEvent)`: Receives an event (implements the queue and backpressure).
- `start()`: Initializes the transport (e.g., opens a connection).
- `stop()`: Cleans up resources.

## Implementations
1. **PythonCallbackTransport**: For standard SDK callbacks (similar to current behavior).
2. **GeneratorTransport (TokenEmitter)**: For Python generators yielding tokens.
3. **ConsoleTransport**: For CLI usage, printing directly to stdout.

Future transports (SSE, WebSocket) can be added by extending `BaseTransport` without touching the Runtime.
