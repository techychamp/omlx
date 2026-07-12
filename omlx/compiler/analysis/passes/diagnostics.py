# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List
from .base import AnalysisPass
from ..graph import AnalysisGraph

class DiagnosticsPass(AnalysisPass):
    """Flags unsupported operations and missing metadata."""

    def run(self, graph: AnalysisGraph) -> Dict[str, Any]:
        unsupported: List[str] = []

        for node in graph.nodes():
            if node.metadata.get("unsupported", False):
                unsupported.append(f"unsupported_operator:{node.node_type.value}")

        desc = graph.descriptor
        if not desc.tokenizer_family and desc.task in ("chat", "text_generation"):
            unsupported.append("missing_tokenizer")

        return {
            "unsupported": list(set(unsupported))
        }
