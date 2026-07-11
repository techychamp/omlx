# SPDX-License-Identifier: Apache-2.0
"""
Types for OMLX Execution Engine.
"""

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

class ExecutionStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    FALLBACK = "fallback"

@dataclass(frozen=True)
class ExecutionResult:
    """Immutable snapshot of the execution result."""
    status: ExecutionStatus
    model_output: Any
    diagnostics: Optional[Any] = None
    statistics: Optional[Any] = None
    execution_duration_ms: float = 0.0
