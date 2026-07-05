# Streaming Lifecycle Guide

The `StreamSession` is designed to be completely independent of the execution loop. It tracks statistics natively:
- **Duration**: `end_time` - `start_time` (or `current_time` if active).
- **First-Token Latency**: `first_token_time` - `start_time`.
- **Diagnostics**: Keeps an append-only log of warnings and lifecycle event strings.
