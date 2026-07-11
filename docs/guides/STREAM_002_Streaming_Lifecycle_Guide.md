# STREAM-002: Streaming Lifecycle Guide

## Event Sequence
Streaming guarantees a deterministic sequence of events:
1. `SESSION_STARTED`
2. `TOKEN_GENERATED` (n times)
3. `WARNING` (optional, e.g., dropped subscribers)
4. `COMPLETED` or `CANCELLED` or `FAILED`
