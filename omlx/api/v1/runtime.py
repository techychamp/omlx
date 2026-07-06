from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio
from omlx.runtime.builder import RuntimeBuilder as InternalRuntimeBuilder
from omlx.runtime.builder import Runtime as InternalRuntime
from omlx.runtime.feature_flags import FeatureFlags

class RuntimeConfig(BaseModel):
    settings: Dict[str, Any] = Field(default_factory=dict)
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

class Runtime(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    internal_runtime: InternalRuntime = Field(exclude=True)

    def __init__(self, internal_runtime: InternalRuntime, **data):
        super().__init__(internal_runtime=internal_runtime, **data)

    @property
    def state(self):
        return self.internal_runtime.state

    def get_feature_flags(self) -> Dict[str, bool]:
        """Public API to access resolved feature flags."""
        if hasattr(self.internal_runtime, "_feature_flags"):
             return self.internal_runtime._feature_flags.flags
        return {}

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Public API to query active streaming or execution sessions."""
        sessions = []
        if hasattr(self.internal_runtime, "streaming_controller"):
             ctrl = self.internal_runtime.streaming_controller
             if hasattr(ctrl, "sessions"):
                  for s_id, s_obj in ctrl.sessions.items():
                       sessions.append({
                            "session_id": s_id,
                            "status": s_obj.status.value if hasattr(s_obj.status, "value") else str(s_obj.status)
                       })
        return sessions

    def get_tooling(self) -> Any:
        """Returns the centralized tooling registry."""
        from omlx.tooling.framework.unified import get_tooling
        return get_tooling()

class RuntimeBuilder:
    def __init__(self):
        self._config = RuntimeConfig()
        self._internal_builder = InternalRuntimeBuilder()

    def configure(self, settings: Dict[str, Any]) -> 'RuntimeBuilder':
        self._config.settings.update(settings)
        self._internal_builder.with_settings(self._config.settings)
        return self

    def enable(self, feature: str) -> 'RuntimeBuilder':
        self._config.feature_flags[feature] = True
        return self

    def disable(self, feature: str) -> 'RuntimeBuilder':
        self._config.feature_flags[feature] = False
        return self

    def build(self) -> Runtime:
        ff = FeatureFlags.from_env()
        # In a real implementation we would apply self._config.feature_flags to ff
        self._internal_builder.with_feature_flags(ff)
        internal_runtime = self._internal_builder.build()
        return Runtime(internal_runtime=internal_runtime)
