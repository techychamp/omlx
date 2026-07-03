# SPDX-License-Identifier: Apache-2.0
"""
Common return types for generation strategies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


__all__ = ["PrefillResult", "ForwardResult", "PostprocessResult"]


@dataclass
class PrefillResult:
    """Result of the prefill sub-phase."""
    prompt_cache: Any = None
    cached_tokens: int = 0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ForwardResult:
    """Result of the forward pass sub-phase."""
    logits: Any = None
    hidden: Any = None
    token_ids: list[int] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PostprocessResult:
    """Result of the postprocess sub-phase."""
    token_ids: list[int] = field(default_factory=list)
    text: str = ""
    is_final: bool = False
    finish_reason: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)
