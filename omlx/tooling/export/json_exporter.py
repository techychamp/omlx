# SPDX-License-Identifier: Apache-2.0
import json
from typing import Any
from .base_exporter import BaseExporter

class JsonExporter(BaseExporter):
    """Exports compiler artifacts to JSON."""

    def export(self, data: dict[str, Any], **kwargs) -> str:
        indent = kwargs.get("indent", 2)
        return json.dumps(data, indent=indent, default=str)
