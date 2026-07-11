# SPDX-License-Identifier: Apache-2.0

import time
import threading
from typing import List, Optional
from queue import Queue

from .types import StreamingToken, StreamingStatistics, StreamingDiagnostics, StreamCompletion
from .events import StreamingEvent, StreamingEventType

class StreamSession:
    def __init__(self, session_id: str):
        self._session_id = session_id
        self._tokens: List[StreamingToken] = []
        self._events: List[StreamingEvent] = []
        self._is_completed = False
        self._is_cancelled = False
        self._error: Optional[Exception] = None
        self._completion_state: Optional[StreamCompletion] = None

        self._start_time = time.time()
        self._first_token_time = 0.0
        self._end_time = 0.0

        self._warnings: List[str] = []
        self._errors: List[str] = []
        self._lifecycle_events: List[str] = [f"Session {session_id} started."]

        self._lock = threading.Lock()

    @property
    def session_id(self) -> str:
        return self._session_id

    def add_event(self, event: StreamingEvent):
        with self._lock:
            self._events.append(event)
            if event.event_type == StreamingEventType.TOKEN_GENERATED:
                token = event.payload.get("token")
                if token and isinstance(token, StreamingToken):
                    if not (self._is_completed or self._is_cancelled):
                        if not self._tokens:
                            self._first_token_time = time.time()
                        self._tokens.append(token)
            elif event.event_type == StreamingEventType.WARNING:
                self._warnings.append(event.payload.get("message", "Unknown warning"))
            elif event.event_type == StreamingEventType.FAILED:
                self._errors.append(event.payload.get("message", "Unknown error"))
            elif event.event_type in (
                StreamingEventType.SESSION_STARTED,
                StreamingEventType.COMPLETED,
                StreamingEventType.CANCELLED,
                StreamingEventType.FAILED
            ):
                self._lifecycle_events.append(f"Event: {event.event_type.value}")

    def complete(self, state: StreamCompletion, error: Optional[Exception] = None):
        with self._lock:
            if self._is_completed or self._is_cancelled:
                return
            self._is_completed = True
            self._completion_state = state
            self._error = error
            self._end_time = time.time()
            if state == StreamCompletion.CANCELLED:
                self._is_cancelled = True

    def cancel(self):
        self.complete(StreamCompletion.CANCELLED)

    @property
    def is_active(self) -> bool:
        with self._lock:
            return not (self._is_completed or self._is_cancelled)


    def get_events_history(self) -> List[StreamingEvent]:
        """Return a copy of all events emitted so far for replay purposes."""
        with self._lock:
            return list(self._events)

    def get_statistics(self) -> StreamingStatistics:
        with self._lock:
            duration = (self._end_time if self._end_time > 0 else time.time()) - self._start_time
            first_latency = (self._first_token_time - self._start_time) if self._first_token_time > 0 else 0.0

            return StreamingStatistics(
                tokens_emitted=len(self._tokens),
                stream_duration=duration,
                first_token_latency=first_latency,
                completion_latency=duration if self._end_time > 0 else 0.0,
                events_published=len(self._events),
                errors=len(self._errors)
            )

    def get_diagnostics(self) -> StreamingDiagnostics:
        with self._lock:
            return StreamingDiagnostics(
                session_id=self._session_id,
                warnings=list(self._warnings),
                errors=list(self._errors),
                lifecycle_events=list(self._lifecycle_events)
            )
