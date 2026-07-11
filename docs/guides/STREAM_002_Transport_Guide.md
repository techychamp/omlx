# STREAM-002: Transport Guide

## Overview
The `StreamingTransport` class defines an abstraction for external consumers to ingest events without blocking the `Runtime`.

## Included Transports
1. **CallbackTransport**: Uses an internal background thread to invoke python callbacks asynchronously.
2. **GeneratorTransport** (formerly `TokenEmitter`): Provides a blocking `.stream()` iterator for synchronous Python loops.

## Creating Custom Transports
To build a custom transport (e.g. WebSocket, SSE):
1. Inherit from `omlx.runtime.streaming.transports.StreamingTransport`.
2. Implement `on_event(event: StreamingEvent)`.
3. Handle queuing and raise `BackpressureException` if the consumer cannot keep up with the Runtime's throughput.
