# SPDX-License-Identifier: Apache-2.0
"""
Compiler Session
Immutable dataclass representing a full compiler execution run.
"""
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from omlx.tooling.session.replay_session import ReplaySession

@dataclass(frozen=True)
class CompilerSession:
    """Immutable representation of one compiler execution."""
    replay_session: ReplaySession
    trace: Any | None = None
    artifacts: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: tuple[str, ...] = tuple()
    statistics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    compiler_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
