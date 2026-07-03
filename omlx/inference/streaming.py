# SPDX-License-Identifier: Apache-2.0
"""
Streaming structures for incremental generation outputs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from omlx.runtime.metrics import GenerationMetrics


__all__ = ["StreamingDelta"]


@dataclass
class StreamingDelta:
    """A single unit of streaming output from any generation strategy."""
    token_ids: list[int] = field(default_factory=list)
    text: str = ""
    is_final: bool = False
    delta_kind: str = "token"       # 'token', 'block', 'verified_block'
    metrics_snapshot: GenerationMetrics | None = None
    finish_reason: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
