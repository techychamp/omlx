from typing import Dict, List, Set, Tuple
from .graph import PluginDependencyGraph, PluginDependencyNode
from .descriptor import PluginDescriptor
from .versioning import SemanticVersion
import logging

logger = logging.getLogger(__name__)

class PluginDependencyResolver:
    def __init__(self, descriptors: Dict[str, PluginDescriptor]):
        self._descriptors = descriptors

    def resolve(self) -> PluginDependencyGraph:
        nodes: Dict[str, PluginDependencyNode] = {}
        roots: Set[str] = set(self._descriptors.keys())

        # Build initial nodes
        for pid, desc in self._descriptors.items():
            depends_on = set()
            optional_deps = set()

            for dep_id, dep_version in desc.dependencies.items():
                if dep_id in self._descriptors:
                    # In a real implementation we would also check version compatibility here
                    depends_on.add(dep_id)
                    roots.discard(pid) # pid is not a root since it depends on something

            for opt_id, opt_version in desc.optional_dependencies.items():
                if opt_id in self._descriptors:
                    optional_deps.add(opt_id)

            nodes[pid] = PluginDependencyNode(
                plugin_id=pid,
                version=desc.version,
                depends_on=frozenset(depends_on),
                optional_dependencies=frozenset(optional_deps)
            )

        # Update required_by
        for pid, node in list(nodes.items()):
            required_by = set()
            for other_pid, other_node in nodes.items():
                if pid in other_node.depends_on:
                    required_by.add(other_pid)

            # Recreate node with required_by populated
            nodes[pid] = PluginDependencyNode(
                plugin_id=node.plugin_id,
                version=node.version,
                required_by=frozenset(required_by),
                depends_on=node.depends_on,
                optional_dependencies=node.optional_dependencies,
                is_replacement=node.is_replacement
            )

        return PluginDependencyGraph(
            nodes=nodes,
            roots=frozenset(roots),
            metadata={"total_plugins": len(nodes)}
        )
