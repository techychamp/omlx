# SPDX-License-Identifier: Apache-2.0

from typing import Iterator, AsyncIterator, Callable, Generator
import time

from .types import StreamingToken
from .controller import StreamingController
from .emitter import TokenEmitter

_global_controller = None

def get_controller() -> StreamingController:
    global _global_controller
    if _global_controller is None:
        _global_controller = StreamingController()
    return _global_controller

def stream_events(session_id: str, callback: Callable) -> None:
    """Subscribe a callback to a stream session's events."""
    _global_controller.subscribe(session_id, callback)

def get_emitter(session_id: str) -> TokenEmitter:
    """Get a TokenEmitter for a given session."""
    session = _global_controller.get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found.")
    return TokenEmitter(session, _global_controller)

def stream(session_id: str) -> Generator[StreamingToken, None, None]:
    """Blocking generator that yields tokens for a session."""
    emitter = get_emitter(session_id)
    try:
        yield from emitter.stream()
    finally:
        emitter.close()

# Note: stream_async() can be added later if asyncio support is required.
