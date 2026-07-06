# SPDX-License-Identifier: Apache-2.0
"""
Snapshot System
Exports read-only snapshots of runtime state.
"""
from typing import Any, Dict
from omlx.api.v1.runtime import Runtime
from omlx.tooling.session.compiler_session import CompilerSession

class RuntimeSnapshot:
    """Read-only snapshot of runtime state at a point in time."""
    def __init__(self, data: Dict[str, Any]):
        self._data = data

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

class SnapshotManager:
    """Creates snapshots of the runtime."""

    def create_snapshot(self, runtime: Runtime, compiler_session: CompilerSession = None) -> RuntimeSnapshot:
        """Captures a snapshot of the runtime."""
        # Defer import to avoid circular dependency
        from omlx.tooling.framework.unified import get_tooling
        tooling = get_tooling()
        runtime_inspector = tooling.get_inspector("runtime")

        snapshot_data = {}
        if runtime_inspector:
            snapshot_data["configuration"] = runtime_inspector.inspect_configuration(runtime)
            snapshot_data["feature_flags"] = runtime_inspector.inspect_feature_flags(runtime)
            snapshot_data["active_sessions"] = runtime_inspector.inspect_active_sessions(runtime)

        if compiler_session:
             snapshot_data["compiler_artifacts"] = dict(compiler_session.artifacts)
             snapshot_data["compiler_diagnostics"] = compiler_session.diagnostics
             snapshot_data["compiler_statistics"] = dict(compiler_session.statistics)

        return RuntimeSnapshot(snapshot_data)
