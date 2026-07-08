# SPDX-License-Identifier: Apache-2.0
"""
Execution Inspector
Provides read-only methods for inspecting execution objects.
"""
from typing import Any, Dict

class ExecutionInspector:
    """
    Execution Inspector.
    Provides read-only inspection methods for execution artifacts.
    Must never mutate execution state.
    """

    def inspect_schedule(self, schedule: Any) -> Dict[str, Any]:
        """Inspects an ExecutionSchedule."""
        res = {}
        if hasattr(schedule, "execution_groups"):
             res["num_groups"] = len(schedule.execution_groups)
        return res

    def inspect_context(self, context: Any) -> Dict[str, Any]:
        """Inspects an ExecutionContext."""
        return {
            "type": str(type(context))
        }

    def inspect_results(self, results: Any) -> Dict[str, Any]:
        """Inspects ExecutionResults."""
        return {
            "type": str(type(results))
        }
