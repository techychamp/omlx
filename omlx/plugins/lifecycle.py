from typing import Dict, List, Any
import logging
from .descriptor import PluginLifecycleState

logger = logging.getLogger(__name__)

class PluginLifecycleMonitor:
    def __init__(self):
        self._state_history: Dict[str, List[PluginLifecycleState]] = {}
        self._counts: Dict[PluginLifecycleState, int] = {state: 0 for state in PluginLifecycleState}

    def record_transition(self, plugin_id: str, new_state: PluginLifecycleState) -> None:
        if plugin_id not in self._state_history:
            self._state_history[plugin_id] = []
        self._state_history[plugin_id].append(new_state)
        self._counts[new_state] += 1

    def get_history(self, plugin_id: str) -> List[PluginLifecycleState]:
        return self._state_history.get(plugin_id, [])

    def get_statistics(self) -> Dict[str, int]:
        return {state.name: count for state, count in self._counts.items()}

    def generate_report(self) -> Dict[str, Any]:
        return {
            "statistics": self.get_statistics(),
            "history": {pid: [s.name for s in history] for pid, history in self._state_history.items()}
        }
