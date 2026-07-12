# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict
from .base import AnalysisPass
from ..graph import AnalysisGraph

class SemanticAnalysisPass(AnalysisPass):
    """Answers: What does this graph mean?"""

    def run(self, graph: AnalysisGraph) -> Dict[str, Any]:
        traits = {
            "has_generative_loop": False,
            "has_encoder_decoder": False,
            "has_routing_logic": False,
            "is_pure_encoder": False
        }

        # We can infer meaning by looking at the node types and task
        if graph.descriptor.task in ("chat", "text_generation", "image_generation"):
            traits["has_generative_loop"] = True

        if graph.descriptor.task == "embedding":
            traits["is_pure_encoder"] = True

        for node in graph.nodes():
            if node.node_type.value == "routing":
                traits["has_routing_logic"] = True
            if node.node_type.value == "cross_attention" or node.metadata.get("cross_attention"):
                traits["has_encoder_decoder"] = True

        return traits
