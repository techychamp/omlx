# SPDX-License-Identifier: Apache-2.0
from typing import Any
from .base_exporter import BaseExporter

class DotExporter(BaseExporter):
    """Exports graph data to GraphViz DOT format."""

    def export(self, data: dict[str, Any], **kwargs) -> str:
        """
        Expects data to be a standardized graph dict:
        {
            "nodes": {"id1": {"label": "N1"}, ...},
            "edges": [{"source": "id1", "target": "id2", "label": "E1"}, ...]
        }
        """
        lines = ["digraph CompilerGraph {"]
        lines.append("  node [shape=box];")

        nodes = data.get("nodes", {})
        for node_id, node_data in nodes.items():
            label = node_data.get("label", node_id)
            lines.append(f'  "{node_id}" [label="{label}"];')

        edges = data.get("edges", [])
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            label = edge.get("label", "")
            lines.append(f'  "{src}" -> "{tgt}" [label="{label}"];')

        lines.append("}")
        return "\n".join(lines)
