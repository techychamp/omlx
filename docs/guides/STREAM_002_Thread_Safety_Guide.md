# STREAM-002: Thread Safety Guide

## Principles
1. **Isolation**: Transports handle their own locking. The `Runtime` thread never shares mutable state with the transport threads.
2. **Controller Locking**: The `StreamingController` uses `threading.Lock()` when modifying `_sessions` and `_subscribers`.
3. **Warning Delegation**: When dropping a subscriber, the controller fires a warning event on a separate daemon thread to avoid re-entrant lock issues or recursive publishing.
