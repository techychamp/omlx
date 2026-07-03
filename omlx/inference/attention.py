# SPDX-License-Identifier: Apache-2.0
"""
Attention descriptors for generation strategies.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


__all__ = ["AttentionMode", "AttentionDescriptor"]


class AttentionMode(enum.Enum):
    """Supported attention modes."""
    CAUSAL = "causal"
    DIFFUSION = "diffusion"
    VERIFY = "verify"
    FUTURE = "future"


@dataclass
class AttentionDescriptor:
    """Kernel-agnostic description of attention behavior.
    
    Strategies construct this to describe what kind of attention is needed.
    The model or Metal kernel decides how to materialise it.
    """
    mode: AttentionMode
    seq_len: int
    cache_len: int
    causal: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
