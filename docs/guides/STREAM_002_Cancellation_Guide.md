# STREAM-002: Cancellation Guide

## Mechanism
1. A client calls `controller.cancel_session(session_id)`.
2. The `StreamSession` is marked with `is_active = False` and state `CANCELLED`.
3. The `Runtime.generate` decode loop explicitly checks `if not session.is_active:` and safely breaks execution at the start of the next token step.
4. A `CANCELLED` event is propagated through transports.
