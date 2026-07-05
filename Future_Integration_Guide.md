# Future Integration Guide

When `BACKEND-005` implements `MLXAdapter.execute()`:

1. Obtain the `session_id` from the `ExecutionContext` (we may need to add it there).
2. Inside the MLX step loop, decode the token locally.
3. Call `get_controller().publish_event(session_id, StreamingEvent(TOKEN_GENERATED, ...))`.
4. Ensure no mutable references are passed to `StreamingToken`.
5. Upon successful generation loop termination, call `complete_session(session_id, SUCCESS)`.
