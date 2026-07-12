from typing import Dict, List, Set, Any
from omlx.compiler.ir.core import Node, Edge
from omlx.compiler.artifacts import CompilerArtifact

class Graph(CompilerArtifact):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.graph_version: int = 1
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self._type_counters: Dict[str, int] = {}

    def generate_id(self, node_type: str) -> str:
        count = self._type_counters.get(node_type, 0) + 1
        self._type_counters[node_type] = count
        return f"{node_type}_{count:03d}"

    def add_node(self, node: Node):
        if not node.id:
            node.id = self.generate_id(node.type)
        elif node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists")

        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        if edge.source_node not in self.nodes:
            raise ValueError(f"Source node {edge.source_node} not found")
        if edge.target_node not in self.nodes:
            raise ValueError(f"Target node {edge.target_node} not found")
        self.edges.append(edge)

    def get_node(self, node_id: str) -> Node:
        if node_id not in self.nodes:
            raise KeyError(f"Node {node_id} not found")
        return self.nodes[node_id]

    def topological_sort(self) -> List[Node]:
        in_degree = {node_id: 0 for node_id in self.nodes}
        adj = {node_id: [] for node_id in self.nodes}

        for edge in self.edges:
            in_degree[edge.target_node] += 1
            adj[edge.source_node].append(edge.target_node)

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(self.nodes[node_id])

            for neighbor in adj[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.nodes):
            raise ValueError("Graph contains a cycle")

        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "generator": self.generator,
            "hash": self.hash,
            "created_at": self.created_at,
            "compiler_version": self.compiler_version,
            "graph_version": self.graph_version,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges]
        }
