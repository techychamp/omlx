import time
from typing import Dict, Any

from omlx.framework.queue.manager import QueueManager
from omlx.framework.queue.artifacts import QueueEntry, QueueStatistics

def capture_queue_metrics(manager: QueueManager) -> QueueStatistics:
    """
    Passively captures immutable statistics from the queue manager.
    Does not modify queue state.
    """
    avg_wait = 0.0
    # Access internal tracking properties (thread-safe properties ideally used)
    # Using the manager's properties guarantees consistency.
    if manager._total_dequeued > 0:
        avg_wait = manager._total_wait_time / manager._total_dequeued

    return QueueStatistics(
        queue_id=manager.descriptor.queue_id,
        current_depth=manager.current_depth,
        total_admitted=manager._total_admitted,
        total_dequeued=manager._total_dequeued,
        average_wait_time=avg_wait,
        timestamp=time.time()
    )

def record_queue_latency(entry: QueueEntry) -> float:
    """
    Calculates the latency (time spent in queue) for a specific queue entry.
    This is typically called upon dequeue or execution handoff.
    """
    return time.time() - entry.admitted_at
