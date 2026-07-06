# SPDX-License-Identifier: Apache-2.0

import threading
import uuid
import time

from .transports import StreamingTransport, BackpressureException
from typing import Dict, List, Optional, Callable, Union


from .session import StreamSession
from .events import StreamingEvent, StreamingEventType
from .types import StreamCompletion

class StreamingController:
    def __init__(self):
        self._sessions: Dict[str, StreamSession] = {}
        self._lock = threading.Lock()
        self._subscribers: Dict[str, List[Union[Callable[[StreamingEvent], None], StreamingTransport]]] = {}

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

    def subscribe(self, session_id: str, subscriber: Union[Callable[[StreamingEvent], None], StreamingTransport], replay: bool = False):
        with self._lock:
            if session_id in self._subscribers:
                self._subscribers[session_id].append(subscriber)

        session = self.get_session(session_id)
        if session and replay:
            history = session.get_events_history()
            for event in history:
                try:
                    if hasattr(subscriber, 'on_event'):
                        subscriber.on_event(event)
                    else:
                        subscriber(event)
                except BackpressureException:
                    self.unsubscribe(session_id, subscriber)
                    self.publish_event(session_id, StreamingEvent(
                        event_type=StreamingEventType.WARNING,
                        timestamp=time.time(),
                        payload={"message": "Subscriber dropped during replay due to backpressure"}
                    ))
                    break
                except Exception:
                    pass

    def unsubscribe(self, session_id: str, subscriber: Union[Callable[[StreamingEvent], None], StreamingTransport]):
        with self._lock:
            if session_id in self._subscribers:
                if subscriber in self._subscribers[session_id]:
                    self._subscribers[session_id].remove(subscriber)

    def publish_event(self, session_id: str, event: StreamingEvent):
        with self._lock:
            session = self._sessions.get(session_id)
            subscribers = list(self._subscribers.get(session_id, []))

        if session:
            session.add_event(event)

        failed_subscribers = []
        for sub in subscribers:
            try:
                if hasattr(sub, 'on_event'):
                    sub.on_event(event)
                else:
                    sub(event)
            except BackpressureException:
                failed_subscribers.append(sub)
            except Exception:
                pass # Ignore other subscriber errors

        if failed_subscribers:
            for sub in failed_subscribers:
                self.unsubscribe(session_id, sub)

            # Use another thread to publish a warning so we don't recurse here directly
            def _publish_warning():
                self.publish_event(session_id, StreamingEvent(
                    event_type=StreamingEventType.WARNING,
                    timestamp=time.time(),
                    payload={"message": f"Dropped {len(failed_subscribers)} subscriber(s) due to backpressure"}
                ))
            threading.Thread(target=_publish_warning, daemon=True).start()


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
