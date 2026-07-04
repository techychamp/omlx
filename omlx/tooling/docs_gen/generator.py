# SPDX-License-Identifier: Apache-2.0
"""
Documentation Generator
Automatically generates markdown documentation from compiler metadata.
"""
from typing import Any
from omlx.tooling.export.markdown_exporter import MarkdownExporter

class DocsGenerator:
    """Generates markdown documentation for compiler components."""

    def __init__(self):
        self.md_exporter = MarkdownExporter()

    def generate_registry_docs(self, registry_metadata: dict[str, Any]) -> str:
        """Generates documentation for a registry based on introspection data."""
        return self.md_exporter.export(registry_metadata, title="Compiler Registry Documentation")

    def generate_artifact_docs(self, artifact_name: str, artifact_data: dict[str, Any]) -> str:
        """Generates documentation for a specific compiler artifact (e.g. ExecutionPlan)."""
        return self.md_exporter.export(artifact_data, title=f"{artifact_name} Documentation")
