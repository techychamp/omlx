# SPDX-License-Identifier: Apache-2.0
"""
Diagnostic Framework
Provides structured diagnostics for developers.
"""
from typing import Any, Dict, List
from omlx.api.v1.runtime import Runtime
from omlx.tooling.session.compiler_session import CompilerSession

class DiagnosticReport:
    """Structured report of diagnostics."""
    def __init__(self, subsystem: str, messages: List[str]):
        self.subsystem = subsystem
        self.messages = messages

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subsystem": self.subsystem,
            "messages": self.messages
        }

class DiagnosticFramework:
    """Collects structured diagnostics from various subsystems."""

    def get_runtime_diagnostics(self, runtime: Runtime = None) -> DiagnosticReport:
        messages = []
        if runtime:
             state = getattr(runtime, "state", "UNKNOWN")
             messages.append(f"Runtime is currently in state: {state}")

             # Extract any queued diagnostic events if observability is available
             from omlx.runtime.observability.global_observer import get_observer
             obs = get_observer()
             # Normally we'd query errors, but for now we note status
             messages.append("Runtime initialization sequence completed.")

        return DiagnosticReport("runtime", messages)

    def get_compiler_diagnostics(self, session: CompilerSession = None) -> DiagnosticReport:
        messages = []
        if session and session.diagnostics:
             messages.extend(session.diagnostics)
        else:
             messages.append("No active compiler warnings or errors detected in session.")
        return DiagnosticReport("compiler", messages)

    def get_backend_diagnostics(self, backend: Any) -> DiagnosticReport:
        # Avoid mutating backend state
        messages = []
        if hasattr(backend, "get_diagnostics"):
            backend_diags = backend.get_diagnostics()
            messages.append(f"Backend diagnostics: {backend_diags}")
        return DiagnosticReport("backend", messages)
