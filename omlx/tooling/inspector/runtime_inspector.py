# SPDX-License-Identifier: Apache-2.0
"""
Runtime Inspector
Provides read-only methods for inspecting runtime objects.
"""
from typing import Any, Dict
from omlx.api.v1.runtime import Runtime

class RuntimeInspector:
    """
    Runtime Inspector.
    Provides read-only inspection methods for runtime objects.
    Must never mutate runtime state.
    """

    def inspect_configuration(self, runtime: Runtime) -> Dict[str, Any]:
        """Returns the current runtime configuration."""
        # Using state as a proxy for config for now, since it is a safe read-only access
        return {
            "state": runtime.state.value if hasattr(runtime.state, "value") else str(runtime.state)
        }

    def inspect_active_sessions(self, runtime: Runtime) -> list[Dict[str, Any]]:
        """Returns info about active sessions."""
        sessions = []
        if hasattr(runtime.internal_runtime, "streaming_controller"):
             ctrl = runtime.internal_runtime.streaming_controller
             if hasattr(ctrl, "sessions"):
                  for s_id, s_obj in ctrl.sessions.items():
                       sessions.append({
                            "session_id": s_id,
                            "status": s_obj.status.value if hasattr(s_obj.status, "value") else str(s_obj.status)
                       })
        return sessions

    def inspect_feature_flags(self, runtime: Runtime) -> Dict[str, bool]:
        """Returns the feature flags for the runtime."""
        # Accessing private attribute strictly for developer inspection.
        # This does not mutate state.
        try:
            return runtime.internal_runtime._feature_flags.flags if hasattr(runtime.internal_runtime, "_feature_flags") else {}
        except Exception:
             return {}
