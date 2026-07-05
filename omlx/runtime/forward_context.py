# SPDX-License-Identifier: Apache-2.0
"""
Forward pass context encapsulating all arguments needed for a forward pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from omlx.inference.attention import AttentionDescriptor


__all__ = ["ForwardContext"]


@dataclass
class ForwardContext:
    """Encapsulates all arguments needed for a single forward pass.
    
    Avoids argument explosion as more generation strategies are added.
    Each strategy constructs this before calling model.forward().
    """
    cache: Any = None
    attention_descriptor: AttentionDescriptor | None = None
    position_ids: Any = None
    block_info: Any = None
    verification_state: Any = None
    extra: dict[str, Any] = field(default_factory=dict)
