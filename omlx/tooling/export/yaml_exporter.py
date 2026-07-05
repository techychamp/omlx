# SPDX-License-Identifier: Apache-2.0
from typing import Any
from .base_exporter import BaseExporter

class YamlExporter(BaseExporter):
    """Exports compiler artifacts to YAML (requires PyYAML, soft dependency)."""

    def export(self, data: dict[str, Any], **kwargs) -> str:
        try:
            import yaml
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        except ImportError:
            return "# YAML export requires 'pyyaml' package.\n# Please install it via `pip install pyyaml`\n" + str(data)
