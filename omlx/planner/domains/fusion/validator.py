# SPDX-License-Identifier: Apache-2.0
"""
Validator for fusion plans to ensure invariants are held.
"""

from .artifacts import FusionPlan
from omlx.runtime.scheduling.artifacts import DependencyGraph

class FusionValidator:
    """
    Validates a generated FusionPlan against a source graph.
    """

    def validate(self, plan: FusionPlan, graph: DependencyGraph) -> bool:
        """
        Validates that all nodes referenced in the FusionPlan exist in the graph,
        and that a node doesn't belong to multiple conflicting groups.
        """
        seen_nodes = set()
        for group in plan.groups:
            for node_id in group.node_ids:
                if node_id not in graph.operations:
                    return False
                if node_id in seen_nodes:
                    return False
                seen_nodes.add(node_id)
        return True
