# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Any, Optional, Dict
from enum import Enum

class StreamingEventType(Enum):
    SESSION_STARTED = "SessionStarted"
    TOKEN_GENERATED = "TokenGenerated"
    PARTIAL_RESPONSE_UPDATED = "PartialResponseUpdated"
    EXECUTION_PROGRESS = "ExecutionProgress"
    STATISTICS_UPDATED = "StatisticsUpdated"
    WARNING = "Warning"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    FAILED = "Failed"

@dataclass(frozen=True)
class StreamingEvent:
    event_type: StreamingEventType
    timestamp: float
    payload: Dict[str, Any]
