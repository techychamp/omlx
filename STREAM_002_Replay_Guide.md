# STREAM-002: Replay Guide

## Overview
Replay ensures that clients who connect mid-generation (e.g., refreshing a GUI) can retrieve the history of tokens generated so far.

## Implementation Details
1. **History Tracking**: The `StreamSession` keeps a copy of all emitted `StreamingEvent`s using `get_events_history()`.
2. **Late Subscription**: When calling `controller.subscribe(..., replay=True)`, the controller pulls the history and immediately calls `transport.on_event()` for every historical event before fully attaching the subscriber for live events.
3. **Thread Safety**: The history retrieval is locked, ensuring a consistent snapshot without dropping concurrent live tokens.
