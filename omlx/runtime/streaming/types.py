# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List
from enum import Enum

@dataclass(frozen=True)
class StreamingToken:
    token_id: int
    decoded_text: str
    timestamp: float
    sequence_index: int
    metadata: Optional[Dict[str, Any]] = None

@dataclass(frozen=True)
class StreamingStatistics:
    tokens_emitted: int
    stream_duration: float
    first_token_latency: float
    completion_latency: float
    events_published: int
    errors: int

@dataclass(frozen=True)
class StreamingDiagnostics:
    session_id: str
    warnings: List[str]
    errors: List[str]
    lifecycle_events: List[str]

class StreamCompletion(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CANCELLED = "CANCELLED"
