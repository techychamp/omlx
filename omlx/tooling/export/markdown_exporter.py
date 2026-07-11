# SPDX-License-Identifier: Apache-2.0
from typing import Any
from .base_exporter import BaseExporter

class MarkdownExporter(BaseExporter):
    """Exports compiler artifacts to developer-readable Markdown."""

    def export(self, data: dict[str, Any], **kwargs) -> str:
        title = kwargs.get("title", "Compiler Artifact")
        lines = [f"# {title}", ""]

        # very basic dict to md table/list
        for k, v in data.items():
            if isinstance(v, dict) and not v:
                lines.append(f"**{k}**: (empty dict)")
            elif isinstance(v, (list, tuple)) and not v:
                lines.append(f"**{k}**: (empty list)")
            elif isinstance(v, dict):
                lines.append(f"## {k}")
                for sub_k, sub_v in v.items():
                    lines.append(f"- **{sub_k}**: `{sub_v}`")
                lines.append("")
            elif isinstance(v, (list, tuple)):
                lines.append(f"## {k}")
                for item in v:
                    lines.append(f"- `{item}`")
                lines.append("")
            else:
                lines.append(f"**{k}**: `{v}`")

        return "\n".join(lines)
