# SPDX-License-Identifier: Apache-2.0

import threading
import uuid
import time
from typing import Dict, List, Optional, Callable

from .session import StreamSession
from .events import StreamingEvent, StreamingEventType
from .types import StreamCompletion

class StreamingController:
    def __init__(self):
        self._sessions: Dict[str, StreamSession] = {}
        self._lock = threading.Lock()
        self._subscribers: Dict[str, List[Callable[[StreamingEvent], None]]] = {}

    def create_session(self) -> StreamSession:
        session_id = str(uuid.uuid4())
        session = StreamSession(session_id)
        with self._lock:
            self._sessions[session_id] = session
            self._subscribers[session_id] = []

        self.publish_event(session_id, StreamingEvent(
            event_type=StreamingEventType.SESSION_STARTED,
            timestamp=time.time(),
            payload={"session_id": session_id}
        ))

        return session

    def get_session(self, session_id: str) -> Optional[StreamSession]:
        with self._lock:
            return self._sessions.get(session_id)

    def subscribe(self, session_id: str, callback: Callable[[StreamingEvent], None]):
        with self._lock:
            if session_id in self._subscribers:
                self._subscribers[session_id].append(callback)

    def unsubscribe(self, session_id: str, callback: Callable[[StreamingEvent], None]):
        with self._lock:
            if session_id in self._subscribers:
                if callback in self._subscribers[session_id]:
                    self._subscribers[session_id].remove(callback)

    def publish_event(self, session_id: str, event: StreamingEvent):
        from omlx.runtime.observability import get_observer

        with self._lock:
            session = self._sessions.get(session_id)
            subscribers = list(self._subscribers.get(session_id, []))

        if session:
            session.add_event(event)

        # Record to observer
        get_observer().trace_builder.record(
            phase="Streaming",
            component="Controller",
            operation=event.event_type.value,
            duration_sec=0,
            metadata=event.payload
        )
        get_observer().timeline_builder.record(
            event_id=str(uuid.uuid4()),
            timestamp=event.timestamp,
            phase="Streaming",
            duration_sec=0,
            session_id=session_id,
            metadata={"event_type": event.event_type.value}
        )

        for sub in subscribers:
            try:
                sub(event)
            except Exception:
                pass # Ignore subscriber errors


    def cancel_session(self, session_id: str):
        session = self.get_session(session_id)
        if session:
            session.cancel()
            self.publish_event(session_id, StreamingEvent(
                event_type=StreamingEventType.CANCELLED,
                timestamp=time.time(),
                payload={"session_id": session_id}
            ))

    def complete_session(self, session_id: str, state: StreamCompletion, error: Optional[Exception] = None):
        session = self.get_session(session_id)
        if session:
            session.complete(state, error)
            event_type = StreamingEventType.COMPLETED if state == StreamCompletion.SUCCESS else StreamingEventType.FAILED
            self.publish_event(session_id, StreamingEvent(
                event_type=event_type,
                timestamp=time.time(),
                payload={"session_id": session_id, "state": state.value, "error": str(error) if error else None}
            ))

    def cleanup_session(self, session_id: str):
        with self._lock:
            self._sessions.pop(session_id, None)
            self._subscribers.pop(session_id, None)
