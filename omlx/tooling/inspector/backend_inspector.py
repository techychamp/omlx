# SPDX-License-Identifier: Apache-2.0
"""
Backend Inspector
Provides read-only methods for inspecting backends.
"""
from typing import Any, Dict

class BackendInspector:
    """
    Backend Inspector.
    Provides read-only inspection methods for backends.
    Must never mutate backend state.
    """

    def inspect_capabilities(self, backend: Any) -> Dict[str, Any]:
        """Inspects backend capabilities."""
        if hasattr(backend, "get_capabilities"):
            return backend.get_capabilities()
        return {}

    def inspect_diagnostics(self, backend: Any) -> Dict[str, Any]:
        """Inspects backend diagnostics."""
        if hasattr(backend, "get_diagnostics"):
            return backend.get_diagnostics()
        return {}
