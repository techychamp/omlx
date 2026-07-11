# Replay Report

## Concept
Subscribers connecting after generation has started (or finished) can request a replay of the stream.

## Implementation
1. **Bounded History**: `StreamSession` will store emitted events up to a maximum limit (inherently bounded by max_tokens).
2. **Replay Execution**: When a transport subscribes with `replay=True`, the `StreamingController` fetches the event history from the `StreamSession` and immediately pushes these events to the transport's queue before fully attaching it for live events.
3. **Thread Safety**: Handled via `StreamSession` locks to ensure a consistent snapshot of history is replayed without missing concurrent live events.
