from dataclasses import dataclass, field
from typing import Dict, List, Set, Any, Optional

@dataclass(frozen=True)
class PluginDependencyNode:
    plugin_id: str
    version: str
    required_by: frozenset[str] = field(default_factory=frozenset)
    depends_on: frozenset[str] = field(default_factory=frozenset)
    optional_dependencies: frozenset[str] = field(default_factory=frozenset)
    is_replacement: bool = False

@dataclass(frozen=True)
class PluginDependencyGraph:
    nodes: Dict[str, PluginDependencyNode]
    roots: frozenset[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_initialization_order(self) -> List[str]:
        # Perform topological sort from ALL nodes, not just roots
        visited: Set[str] = set()
        visiting: Set[str] = set() # To catch cycles
        order: List[str] = []

        def dfs(node_id: str):
            if node_id in visited:
                return
            if node_id in visiting:
                raise ValueError(f"Circular dependency detected involving {node_id}")

            visiting.add(node_id)
            node = self.nodes.get(node_id)
            if node:
                for dep in node.depends_on:
                    dfs(dep)

            visiting.remove(node_id)
            visited.add(node_id)
            order.append(node_id)

        for node_id in self.nodes.keys():
            dfs(node_id)

        return order
