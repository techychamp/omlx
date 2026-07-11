# SPDX-License-Identifier: Apache-2.0
"""
Runtime Inspector
Provides read-only methods for inspecting runtime objects.
"""
from typing import Any, Dict
from omlx.api.v1.runtime import RuntimeService

class RuntimeInspector:
    """
    Runtime Inspector.
    Provides read-only inspection methods for runtime objects.
    Must never mutate runtime state.
    """

    def inspect_configuration(self, runtime: RuntimeService) -> Dict[str, Any]:
        """Returns the current runtime configuration."""
        # Using state as a proxy for config for now, since it is a safe read-only access
        return {
            "state": runtime.status if hasattr(runtime, "status") else str(runtime.status)
        }

    def inspect_active_sessions(self, runtime: RuntimeService) -> list[Dict[str, Any]]:
        """Returns info about active sessions via public API."""
        if hasattr(runtime, "get_active_sessions"):
            return runtime.get_active_sessions()
        return []

    def inspect_feature_flags(self, runtime: RuntimeService) -> Dict[str, bool]:
        """Returns the feature flags for the runtime via public API."""
        if hasattr(runtime, "get_feature_flags"):
            return runtime.get_feature_flags()
        return {}
