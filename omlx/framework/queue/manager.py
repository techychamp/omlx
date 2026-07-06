from typing import Any
import threading
import uuid
from typing import Optional, List, Dict
from collections import deque

from omlx.framework.queue.artifacts import QueueDescriptor, QueueEntry, QueueSession
from omlx.framework.queue.admission import QueueAdmissionController

class QueueManager:
    """
    Manages the lifecycle, ordering, and state of queued requests.
    Thread-safe implementation using threading locks.
    Does not execute requests.
    """
    def __init__(self, queue_id: str = "default", max_capacity: int = 1000, distributed: bool = False):
        self.descriptor = QueueDescriptor(
            queue_id=queue_id,
            max_capacity=max_capacity,
            prioritization_supported=True,
            distributed=distributed
        )
        self.admission_controller = QueueAdmissionController()

        # Thread-safe state
        self._lock = threading.Lock()

        # Simple FIFO queue implementation.
        # In a priority queue implementation, we might use heapq, but a simple deque is fine for the architectural foundation.
        self._queue: deque[QueueSession] = deque()
        self._sessions: Dict[str, QueueSession] = {}

        # Stats tracking
        self._total_admitted = 0
        self._total_dequeued = 0
        self._total_wait_time = 0.0

    def enqueue(self, request: Any, priority: int = 0) -> QueueSession:
        """Admits a request and enqueues it, returning a QueueSession."""
        entry = self.admission_controller.admit_request(request, priority=priority)
        session_id = str(uuid.uuid4())

        session = QueueSession(
            session_id=session_id,
            entry=entry,
            descriptor=self.descriptor,
            status="queued"
        )

        with self._lock:
            if len(self._queue) >= self.descriptor.max_capacity:
                raise RuntimeError(f"Queue {self.descriptor.queue_id} is at maximum capacity ({self.descriptor.max_capacity})")

            # Simple insertion based on priority. Higher number = higher priority.
            # O(N) insertion is fine for foundational architecture, would optimize for production.
            inserted = False
            for i, existing_session in enumerate(self._queue):
                if session.entry.priority > existing_session.entry.priority:
                    self._queue.insert(i, session)
                    inserted = True
                    break

            if not inserted:
                self._queue.append(session)

            self._sessions[session_id] = session
            self._total_admitted += 1

        return session

    def dequeue(self) -> Optional[QueueSession]:
        """Removes and returns the next request from the queue for handoff to Runtime."""
        import time

        with self._lock:
            if not self._queue:
                return None

            session = self._queue.popleft()

            # Create a new updated session (immutable)
            updated_session = QueueSession(
                session_id=session.session_id,
                entry=session.entry,
                descriptor=session.descriptor,
                status="ready_for_execution"
            )

            self._sessions[session.session_id] = updated_session

            # Update stats
            self._total_dequeued += 1
            wait_time = time.time() - session.entry.admitted_at
            self._total_wait_time += wait_time

            return updated_session

    def get_session(self, session_id: str) -> Optional[QueueSession]:
        """Retrieves the current state of a queue session."""
        with self._lock:
            return self._sessions.get(session_id)

    def remove_session(self, session_id: str) -> bool:
        """Removes a session entirely (e.g., after successful handoff or cancellation)."""
        with self._lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                if session in self._queue:
                    self._queue.remove(session)
                del self._sessions[session_id]
                return True
            return False

    @property
    def current_depth(self) -> int:
        """Returns the current number of items in the queue."""
        with self._lock:
            return len(self._queue)
