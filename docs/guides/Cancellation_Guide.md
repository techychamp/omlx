# Cancellation Guide

- Streaming cancellation acts immediately by locking the state to `StreamCompletion.CANCELLED`.
- It triggers a `CANCELLED` event, causing the `TokenEmitter` stream to break and return.
- To cancel an ongoing execution from a backend perspective (future integration), backend adapters should listen to the `CANCELLED` event and abort their kernel loops without crashing the engine.
