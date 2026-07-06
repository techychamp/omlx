from typing import List, Any, Dict
from pydantic import BaseModel, Field
import asyncio
from omlx.runtime.builder import RuntimeBuilder as InternalRuntimeBuilder
from omlx.runtime.feature_flags import FeatureFlags

from omlx.api.v1.generation import GenerationService
from omlx.api.v1.model import ModelService
from omlx.api.v1.compiler import CompilerService

class RuntimeConfig(BaseModel):
    settings: Dict[str, Any] = Field(default_factory=dict)
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

class RuntimeService:
    def __init__(self, internal_runtime):
        self._internal = internal_runtime
        self._generation = GenerationService(self._internal)
        self._model = ModelService(self._internal)

    @property
    def status(self) -> str:
        if hasattr(self._internal, 'state') and hasattr(self._internal.state, 'value'):
            return self._internal.state.value
        return "unknown"

    @property
    def generation(self) -> GenerationService:
        return self._generation

    @property
    def models(self) -> ModelService:
        return self._model

    def get_feature_flags(self) -> Dict[str, bool]:
        """Public API to access resolved feature flags."""
        if hasattr(self._internal, "_feature_flags"):
             return self._internal._feature_flags.flags
        return {}

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Public API to query active streaming or execution sessions."""
        sessions = []
        if hasattr(self._internal, "streaming_controller"):
             ctrl = self._internal.streaming_controller
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
        self._settings = {}
        # Changed to construct FeatureFlags explicitly
        self._feature_flags = FeatureFlags()
        self._internal_builder = InternalRuntimeBuilder()

    def configure(self, settings: Dict[str, Any]) -> 'RuntimeBuilder':
        self._settings.update(settings)
        self._internal_builder.with_settings(self._settings)
        return self

    def enable(self, feature: str) -> 'RuntimeBuilder':
        if hasattr(self._feature_flags, feature):
            setattr(self._feature_flags, feature, True)
        return self

    def disable(self, feature: str) -> 'RuntimeBuilder':
        if hasattr(self._feature_flags, feature):
            setattr(self._feature_flags, feature, False)
        return self

    def build(self) -> RuntimeService:
        self._internal_builder.with_feature_flags(self._feature_flags)
        internal_runtime = self._internal_builder.build()
        return RuntimeService(internal_runtime)
