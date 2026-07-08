from typing import List, Any, Dict
from pydantic import BaseModel, Field
import asyncio
from omlx.runtime.builder import RuntimeBuilder as InternalRuntimeBuilder
from omlx.runtime.feature_flags import FeatureFlags

from omlx.api.v1.generation import GenerationService
from omlx.api.v1.model import ModelService
from omlx.api.v1.compiler import CompilerService
from omlx.framework.queue.api import QueueAPI

class RuntimeConfig(BaseModel):
    settings: Dict[str, Any] = Field(default_factory=dict)
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

class RuntimeService:
    def __init__(self, internal_runtime):
        self._internal = internal_runtime
        self._generation = GenerationService(self._internal)
        self._model = ModelService(self._internal)
        if hasattr(self._internal, 'queue_manager') and self._internal.queue_manager:
            self._queue_api = QueueAPI(self._internal.queue_manager)
        else:
            self._queue_api = None

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



    def get_queue_statistics(self) -> Dict[str, Any]:
        """Public API to query queue statistics."""
        if self._queue_api:
            stats = self._queue_api.get_statistics()
            return {
                "queue_id": stats.queue_id,
                "current_depth": stats.current_depth,
                "total_admitted": stats.total_admitted,
                "total_dequeued": stats.total_dequeued,
                "average_wait_time": stats.average_wait_time,
                "timestamp": stats.timestamp
            }
        return {}

    def get_queue_diagnostics(self) -> Dict[str, Any]:
        """Public API to query queue diagnostics."""
        if self._queue_api:
            diag = self._queue_api.get_diagnostics()
            return {
                "queue_id": diag.queue_id,
                "is_healthy": diag.is_healthy,
                "last_error": diag.last_error,
                "validation_errors": diag.validation_report.errors if diag.validation_report else [],
                "validation_warnings": diag.validation_report.warnings if diag.validation_report else [],
                "timestamp": diag.timestamp
            }
        return {}

    def get_speculative_statistics(self) -> Dict[str, Any]:
        """Public API to query active speculative execution statistics."""
        stats = {}
        # In a real implementation this would aggregate from active or recent sessions
        # via the internal runtime or an active metrics observer.
        # For now, it provides a stable interface.
        stats["active_speculative_sessions"] = 0
        stats["total_speculative_attempts"] = 0
        stats["total_accepted_tokens"] = 0
        stats["average_acceptance_rate"] = 0.0
        return stats

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
