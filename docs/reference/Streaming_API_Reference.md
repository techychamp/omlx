# Streaming API Reference

### `get_controller() -> StreamingController`
Returns the global `StreamingController` singleton for session management and event publication.

### `stream(session_id: str) -> Generator[StreamingToken, None, None]`
A generator that yields `StreamingToken`s as they are emitted for the given `session_id`.

### `stream_events(session_id: str, callback: Callable[[StreamingEvent], None])`
Subscribes a callback to all events for a specific session.

### `get_emitter(session_id: str) -> TokenEmitter`
Retrieves the underlying `TokenEmitter` object for manual control.

## Events (`StreamingEventType`)
- `SESSION_STARTED`
- `TOKEN_GENERATED`
- `PARTIAL_RESPONSE_UPDATED`
- `EXECUTION_PROGRESS`
- `STATISTICS_UPDATED`
- `WARNING`
- `COMPLETED`
- `CANCELLED`
- `FAILED`
