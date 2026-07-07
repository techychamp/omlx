# SPDX-License-Identifier: Apache-2.0
"""
Queue Inspector
Provides read-only methods for inspecting queue artifacts.
"""
from typing import Any, Dict, Optional
from omlx.framework.queue.artifacts import QueueStatistics, QueueDiagnostics
from omlx.framework.queue.manager import QueueManager

class QueueInspector:
    """
    Queue Inspector.
    Provides read-only inspection methods for queue components.
    Must never mutate queue state.
    """

    def inspect_queue_statistics(self, manager: QueueManager) -> Optional[QueueStatistics]:
        """Returns the current queue statistics using observability endpoints."""
        try:
            from omlx.framework.queue.observability import capture_queue_metrics
            return capture_queue_metrics(manager)
        except Exception:
            return None

    def inspect_queue_diagnostics(self, manager: QueueManager) -> Optional[QueueDiagnostics]:
        """Returns the current queue diagnostics via API endpoints."""
        try:
            from omlx.framework.queue.api import QueueAPI
            api = QueueAPI(manager)
            return api.get_diagnostics()
        except Exception:
            return None

    def inspect_queue_depth(self, manager: QueueManager) -> int:
        """Returns the current depth of the queue."""
        if manager:
             return manager.current_depth
        return 0
