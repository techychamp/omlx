# SPDX-License-Identifier: Apache-2.0
from typing import Any
from .base_exporter import BaseExporter

class MermaidExporter(BaseExporter):
    """Exports graph data to Mermaid.js format."""

    def export(self, data: dict[str, Any], **kwargs) -> str:
        lines = ["graph TD"]

        nodes = data.get("nodes", {})
        for node_id, node_data in nodes.items():
            label = node_data.get("label", node_id)
            lines.append(f'    {node_id}["{label}"]')

        edges = data.get("edges", [])
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            label = edge.get("label", "")
            if label:
                lines.append(f'    {src} -- "{label}" --> {tgt}')
            else:
                lines.append(f'    {src} --> {tgt}')

        return "\n".join(lines)
