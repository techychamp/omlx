# SPDX-License-Identifier: Apache-2.0
"""
RuntimeBuilder and Composition Root implementation.
"""

from __future__ import annotations

import enum
import time
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from .context import RuntimeState
from .events import EventBus
from .feature_flags import FeatureFlags

logger = logging.getLogger("omlx.runtime")


class RuntimeStateEnum(enum.Enum):
    CREATED = "created"
    BOOTSTRAPPING = "bootstrapping"
    INITIALIZING = "initializing"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass(frozen=True)
class RuntimeContext:
    """Immutable snapshot of the runtime context."""
    settings: Any = None
    environment: Any = None
    hardware: Any = None
    capabilities: Any = None
    verification: Any = None
    feature_flags: FeatureFlags = field(default_factory=FeatureFlags)
    registries: Any = None
    planner_references: Any = None
    startup_metadata: dict[str, Any] = field(default_factory=dict)
    version_info: dict[str, str] = field(default_factory=dict)


class Runtime:
    """Central runtime object owning all subsystems.

    This replaces scattered singleton access in the Composition Root architecture.
    """

    def __init__(self, context: RuntimeContext) -> None:
        self.context = context
        self.state = RuntimeStateEnum.CREATED

        # Subsystems
        self.settings: Any = context.settings
        self.feature_flags: FeatureFlags = context.feature_flags
        self.registries: Any = None
        self.plugin_manager: Any = None
        self.verification_framework: Any = context.verification
        self.engine_pool: Any = None
        self.metrics: Any = None
        self.event_bus = EventBus()

    def transition(self, new_state: RuntimeStateEnum) -> None:
        """Safely transition lifecycle states."""
        # Add basic state machine validation here if needed
        self.state = new_state
        logger.debug(f"Runtime state transition: {self.state.value}")


class RuntimeBuilder:
    """Builder for assembling the Runtime object."""

    def __init__(self) -> None:
        self._settings = None
        self._feature_flags = FeatureFlags.from_env()
        self._verification = None
        self._engine_pool = None

    def with_settings(self, settings: Any) -> RuntimeBuilder:
        self._settings = settings
        return self

    def with_feature_flags(self, feature_flags: FeatureFlags) -> RuntimeBuilder:
        self._feature_flags = feature_flags
        return self

    def with_verification(self, verification: Any) -> RuntimeBuilder:
        self._verification = verification
        return self

    def with_engine_pool(self, engine_pool: Any) -> RuntimeBuilder:
        self._engine_pool = engine_pool
        return self

    def build(self) -> Runtime:
        """Construct the immutable context and wire up the Runtime."""
        context = RuntimeContext(
            settings=self._settings,
            feature_flags=self._feature_flags,
            verification=self._verification,
            startup_metadata={"start_time": time.time()}
        )

        runtime = Runtime(context)
        runtime.engine_pool = self._engine_pool
        runtime.transition(RuntimeStateEnum.BOOTSTRAPPING)

        # In a full implementation, registries and plugin manager would be initialized here

        return runtime
