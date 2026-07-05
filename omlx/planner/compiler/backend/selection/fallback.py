# SPDX-License-Identifier: Apache-2.0
"""
Backend Fallback Framework.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

@dataclass(frozen=True)
class FallbackNode:
    backend_id: str
    is_compatible: bool
    reasons: tuple[str, ...] = tuple()

@dataclass(frozen=True)
class FallbackPlan:
    primary_backend: str
    selected_backend: str
    nodes: tuple[FallbackNode, ...]
    is_successful: bool
    diagnostics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
