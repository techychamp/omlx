import uuid
from typing import Any, Dict, Optional
from omlx.framework.queue.artifacts import QueueEntry

class QueueAdmissionController:
    """Handles the admission of requests into the queue framework."""

    def __init__(self):
        # We could inject validation logic here
        pass

    def admit_request(self, request: Any, priority: int = 0, metadata: Optional[Dict[str, Any]] = None) -> QueueEntry:
        """
        Admits a new request and creates an immutable QueueEntry.

        Args:
            request: The generation request or similar execution intent.
            priority: An optional priority level.
            metadata: Additional metadata for queue management.

        Returns:
            An immutable QueueEntry representing the admitted request.
        """
        entry_id = str(uuid.uuid4())

        # Ensure metadata is at least an empty dict
        safe_metadata = metadata or {}

        entry = QueueEntry(
            entry_id=entry_id,
            request=request,
            priority=priority,
            metadata=safe_metadata
        )

        return entry
