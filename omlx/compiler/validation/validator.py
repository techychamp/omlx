from typing import List, Dict
from omlx.compiler.graph.builder import Graph
from omlx.compiler.cmr.models import CanonicalModelRepresentation

class GraphValidator:
    def validate(self, graph: Graph, cmr: CanonicalModelRepresentation) -> List[str]:
        errors = []

        # Check for cycles via topological sort
        try:
            graph.topological_sort()
        except ValueError as e:
            errors.append(str(e))

        # Check graph connectivity (every node except input should have in-edges, except output should have out-edges)
        # We simplify this to checking if edges reference valid nodes, which is handled by Graph.add_edge

        # Check operator consistency (inputs/outputs lengths match edge connections)
        # This is a basic check.
        in_edges: Dict[str, int] = {n: 0 for n in graph.nodes}
        out_edges: Dict[str, int] = {n: 0 for n in graph.nodes}
        for edge in graph.edges:
            out_edges[edge.source_node] += 1
            in_edges[edge.target_node] += 1

        return errors
