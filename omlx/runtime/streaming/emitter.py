# SPDX-License-Identifier: Apache-2.0

import threading
import queue
from typing import Iterator, Optional, Generator

from .types import StreamingToken
from .session import StreamSession
from .events import StreamingEvent, StreamingEventType

class TokenEmitter:
    def __init__(self, session: StreamSession, controller):
        self._session = session
        self._controller = controller
        self._queue: queue.Queue = queue.Queue()
        self._closed = False
        self._lock = threading.Lock()

        # Subscribe to events to populate the queue
        self._controller.subscribe(session.session_id, self._on_event)

    def _on_event(self, event: StreamingEvent):
        if event.event_type == StreamingEventType.TOKEN_GENERATED:
            token_data = event.payload.get("token")
            if token_data and isinstance(token_data, StreamingToken):
                self._queue.put(token_data)
        elif event.event_type in (StreamingEventType.COMPLETED, StreamingEventType.CANCELLED, StreamingEventType.FAILED):
            self._queue.put(None) # Sentinel value for completion

    def stream(self) -> Generator[StreamingToken, None, None]:
        while not self._closed:
            try:
                # Block until a token is available or Sentinel is reached
                token = self._queue.get(timeout=0.1)
                if token is None:
                    break
                yield token
            except queue.Empty:
                with self._lock:
                    if self._closed:
                        break

    def close(self):
        with self._lock:
            self._closed = True
            self._controller.unsubscribe(self._session.session_id, self._on_event)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
