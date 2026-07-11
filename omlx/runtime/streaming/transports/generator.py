# SPDX-License-Identifier: Apache-2.0
import threading
import queue
from typing import Generator, Optional
from .base import StreamingTransport, BackpressureException
from ..events import StreamingEvent, StreamingEventType
from ..types import StreamingToken
class GeneratorTransport(StreamingTransport):
    def __init__(self, max_buffer_size: int = 1000):
        self.max_buffer_size = max_buffer_size
        self._queue = queue.Queue(maxsize=max_buffer_size)
        self._closed = False
        self._lock = threading.Lock()
        self._session_id: Optional[str] = None
        self._controller = None
    def set_context(self, session_id: str, controller) -> None:
        self._session_id = session_id
        self._controller = controller
    def on_event(self, event: StreamingEvent) -> None:
        with self._lock:
            if self._closed: return
        if event.event_type == StreamingEventType.TOKEN_GENERATED:
            token_data = event.payload.get("token")
            if token_data and isinstance(token_data, StreamingToken):
                try: self._queue.put(token_data, block=True, timeout=0.01)
                except queue.Full: raise BackpressureException("GeneratorTransport buffer full")
        elif event.event_type in (StreamingEventType.COMPLETED, StreamingEventType.CANCELLED, StreamingEventType.FAILED):
            try: self._queue.put(None, block=True, timeout=0.1)
            except queue.Full: pass
    def stream(self) -> Generator[StreamingToken, None, None]:
        while not self._closed:
            try:
                token = self._queue.get(timeout=0.1)
                if token is None: break
                yield token
            except queue.Empty:
                with self._lock:
                    if self._closed: break
    def stop(self) -> None:
        with self._lock: self._closed = True
        if self._controller and self._session_id:
             self._controller.unsubscribe(self._session_id, self)
    def close(self): self.stop()
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): self.close()
