# SPDX-License-Identifier: Apache-2.0
from typing import Any
from .base_exporter import BaseExporter

class PlantUMLExporter(BaseExporter):
    """Exports graph data to PlantUML format."""

    def export(self, data: dict[str, Any], **kwargs) -> str:
        lines = ["@startuml"]

        nodes = data.get("nodes", {})
        for node_id, node_data in nodes.items():
            label = node_data.get("label", node_id)
            lines.append(f'rectangle "{label}" as {node_id}')

        edges = data.get("edges", [])
        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            label = edge.get("label", "")
            if label:
                lines.append(f'{src} --> {tgt} : {label}')
            else:
                lines.append(f'{src} --> {tgt}')

        lines.append("@enduml")
        return "\n".join(lines)
