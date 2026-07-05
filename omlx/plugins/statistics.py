from typing import Dict, Any
from .registry import PluginRegistry
from .graph import PluginDependencyGraph
from .lifecycle import PluginLifecycleMonitor

class PluginStatisticsCollector:
    def __init__(self, registry: PluginRegistry, graph: PluginDependencyGraph, monitor: PluginLifecycleMonitor):
        self._registry = registry
        self._graph = graph
        self._monitor = monitor

    def collect(self) -> Dict[str, Any]:
        stats = {
            "plugin_count": len(self._registry._descriptors),
            "dependency_depth": self._calculate_depth(),
            "lifecycle_statistics": self._monitor.get_statistics(),
            "trust_distribution": self._calculate_trust_distribution(),
            "permission_usage": self._calculate_permission_usage(),
            "registry_query_statistics": {} # Placeholder for query stats
        }
        return stats

    def _calculate_depth(self) -> int:
        if not self._graph.roots:
            return 0

        def max_depth(node_id: str, visited: set) -> int:
            if node_id in visited:
                return 0
            visited.add(node_id)
            node = self._graph.nodes.get(node_id)
            if not node or not node.depends_on:
                return 1
            return 1 + max([max_depth(dep, visited.copy()) for dep in node.depends_on])

        return max([max_depth(root, set()) for root in self._graph.roots])

    def _calculate_trust_distribution(self) -> Dict[str, int]:
        dist = {}
        for desc in self._registry._descriptors.values():
            level = desc.trust_level.value
            dist[level] = dist.get(level, 0) + 1
        return dist

    def _calculate_permission_usage(self) -> Dict[str, int]:
        usage = {}
        for desc in self._registry._descriptors.values():
            for perm in desc.permissions:
                usage[perm.value] = usage.get(perm.value, 0) + 1
        return usage
