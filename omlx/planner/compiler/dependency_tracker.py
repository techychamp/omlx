# SPDX-License-Identifier: Apache-2.0
"""
Dependency Tracker for incremental compilation.
"""

import threading
from typing import Dict, Set

class DependencyTracker:
    """Tracks dependencies between compiler artifacts for invalidation."""
    def __init__(self):
        # Maps an upstream artifact key to a set of downstream artifact keys
        self._downstream: Dict[str, Set[str]] = {}
        # Maps a downstream artifact key to a set of upstream artifact keys
        self._upstream: Dict[str, Set[str]] = {}
        self._lock = threading.Lock()

    def record_dependency(self, source_key: str, target_key: str) -> None:
        """Record that target_key depends on source_key."""
        with self._lock:
            if source_key not in self._downstream:
                self._downstream[source_key] = set()
            self._downstream[source_key].add(target_key)

            if target_key not in self._upstream:
                self._upstream[target_key] = set()
            self._upstream[target_key].add(source_key)

    def get_downstream_dependencies(self, key: str) -> Set[str]:
        """Get all artifacts that transitively depend on the given key."""
        with self._lock:
            visited = set()
            self._dfs_downstream(key, visited)
            if key in visited:
                visited.remove(key) # Return only dependents, not the node itself
            return visited

    def _dfs_downstream(self, current_key: str, visited: Set[str]) -> None:
        if current_key in visited:
            return
        visited.add(current_key)
        for dependent in self._downstream.get(current_key, set()):
            self._dfs_downstream(dependent, visited)

    def remove_node(self, key: str) -> None:
        """Remove a node and its direct dependency links."""
        with self._lock:
            # Remove from downstream lists of its upstream dependencies
            for up_node in self._upstream.get(key, set()):
                if up_node in self._downstream and key in self._downstream[up_node]:
                    self._downstream[up_node].remove(key)

            # Remove from upstream lists of its downstream dependencies
            for down_node in self._downstream.get(key, set()):
                if down_node in self._upstream and key in self._upstream[down_node]:
                    self._upstream[down_node].remove(key)

            if key in self._upstream:
                del self._upstream[key]
            if key in self._downstream:
                del self._downstream[key]
