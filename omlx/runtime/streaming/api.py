# SPDX-License-Identifier: Apache-2.0

from typing import Iterator, AsyncIterator, Callable, Generator
import time

from .types import StreamingToken
from .controller import StreamingController
from .transports import GeneratorTransport as TokenEmitter

_global_controller = None

def get_controller() -> StreamingController:
    global _global_controller
    if _global_controller is None:
        _global_controller = StreamingController()
    return _global_controller

def stream_events(session_id: str, callback: Callable, replay: bool = False) -> None:
    """Subscribe a callback to a stream session's events."""
    _global_controller.subscribe(session_id, callback, replay=replay)

def get_emitter(session_id: str) -> TokenEmitter:
    """Get a TokenEmitter for a given session."""
    session = _global_controller.get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found.")
    emitter = TokenEmitter()
    emitter.set_context(session_id, _global_controller)
    _global_controller.subscribe(session_id, emitter)
    return emitter

def stream(session_id: str, replay: bool = False) -> Generator[StreamingToken, None, None]:
    """Blocking generator that yields tokens for a session."""
    session = _global_controller.get_session(session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found.")

    emitter = TokenEmitter()
    emitter.set_context(session_id, _global_controller)
    _global_controller.subscribe(session_id, emitter, replay=replay)

    try:
        yield from emitter.stream()
    finally:
        emitter.close()

# Note: stream_async() can be added later if asyncio support is required.
