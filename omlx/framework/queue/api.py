from typing import Dict, Any, Optional

from omlx.framework.queue.manager import QueueManager
from omlx.framework.queue.artifacts import QueueStatistics, QueueDiagnostics, QueueValidationReport
from omlx.framework.queue.observability import capture_queue_metrics

class QueueAPI:
    """
    Provides public-facing, read-only API access to queue diagnostics and statistics.
    Extends API-004 capabilities without adding queue-specific execution APIs.
    """

    def __init__(self, manager: QueueManager):
        self._manager = manager

    def get_statistics(self) -> QueueStatistics:
        """Returns an immutable snapshot of queue statistics."""
        return capture_queue_metrics(self._manager)

    def get_diagnostics(self) -> QueueDiagnostics:
        """Returns an immutable snapshot of queue health and diagnostics."""
        # Simple health check based on capacity for this foundational version
        is_healthy = self._manager.current_depth < self._manager.descriptor.max_capacity

        validation = QueueValidationReport(
            is_valid=True,
            errors=[],
            warnings=[] if is_healthy else ["Queue is at maximum capacity"]
        )

        return QueueDiagnostics(
            queue_id=self._manager.descriptor.queue_id,
            is_healthy=is_healthy,
            last_error=None,
            validation_report=validation
        )
