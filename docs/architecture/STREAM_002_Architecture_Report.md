# Streaming Architecture Report

## Overview
The upgraded streaming architecture decouples the generation loop from the transport mechanism, ensuring the Runtime remains the sole owner of execution.

## Flow
`Runtime.generate()` -> `StreamingController` -> `StreamSession` -> `StreamingTransport` -> (CLI, GUI, HTTP, etc.)

## Components
1. **Runtime**: Unchanged ownership. Only adds a cancellation check (`if not session.is_active: break`) to terminate early.
2. **StreamingController**: Thread-safe publisher that routes events from the Runtime to registered transports.
3. **StreamSession**: Maintains state, statistics, and a bounded buffer of historical events for replay.
4. **StreamingTransport**: A new abstraction for event delivery.

## Multiple Subscribers & Ordering
Subscribers register their transports with the `StreamingController`. The controller iterates through subscribers and places events in their respective bounded queues, preserving strict deterministic ordering (GenerationStarted -> TokenGenerated... -> GenerationCompleted).
