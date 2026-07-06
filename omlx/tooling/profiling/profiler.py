# SPDX-License-Identifier: Apache-2.0
"""
Profiling Support
Provides developer profiling helpers using Observability.
"""
from typing import Any, Dict
from omlx.runtime.observability.global_observer import get_observer
from omlx.tooling.session.compiler_session import CompilerSession

class DeveloperProfiler:
    """
    Developer Profiler.
    Consumes observability data to provide profiling insights.
    Must never instrument independently.
    """

    def __init__(self):
        self.observer = get_observer()

    def get_compile_time_profile(self, session: CompilerSession = None) -> Dict[str, Any]:
        """Returns compile time profiling data from observability."""
        profile_data = {}
        if session and session.statistics:
             profile_data["total_compile_time_ms"] = session.statistics.get("total_time_ms", 0.0)
             profile_data["phases"] = session.statistics.get("phases", {})
        else:
             # Stub for tests/if no session provided
             profile_data["stub"] = "compile_profile_data"
        return profile_data

    def get_execution_time_profile(self) -> Dict[str, Any]:
         """Returns execution time profiling data from observability."""
         # In a full implementation, we'd query the GlobalObserver for 'Execution' metrics
         return {"stub": "execution_profile_data"}
