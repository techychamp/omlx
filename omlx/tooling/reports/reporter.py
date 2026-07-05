# SPDX-License-Identifier: Apache-2.0
"""
Reporting Engine
Generates detailed reports using the shared reporting infrastructure.
"""
from typing import Any, Protocol, runtime_checkable
from omlx.tooling.session.compiler_session import CompilerSession
from omlx.tooling.introspection.diagnostics import DiagnosticsEngine
import json

@runtime_checkable
class ReportRenderer(Protocol):
    def render(self, report_data: dict[str, Any]) -> str:
        ...

class TextRenderer:
    def render(self, report_data: dict[str, Any]) -> str:
        lines = [f"{report_data.get('title', 'Report')}"]
        lines.append("=" * len(lines[0]))

        for section, data in report_data.get("sections", {}).items():
            lines.append(f"\n{section}:")
            if isinstance(data, dict):
                for k, v in data.items():
                    lines.append(f"  {k}: {v}")
            elif isinstance(data, list):
                for item in data:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"  {data}")

        return "\n".join(lines)

class JsonRenderer:
    def render(self, report_data: dict[str, Any]) -> str:
        return json.dumps(report_data, indent=2, default=str)

class MarkdownRenderer:
    def render(self, report_data: dict[str, Any]) -> str:
        lines = [f"# {report_data.get('title', 'Report')}\n"]

        for section, data in report_data.get("sections", {}).items():
            lines.append(f"## {section}")
            if isinstance(data, dict):
                for k, v in data.items():
                    lines.append(f"- **{k}**: {v}")
            elif isinstance(data, list):
                for item in data:
                    lines.append(f"- {item}")
            else:
                lines.append(f"{data}")
            lines.append("")

        return "\n".join(lines)


class ReportingEngine:
    """Generates structured report models from compiler sessions."""
    def __init__(self, renderer: ReportRenderer | None = None):
        self.diagnostics_engine = DiagnosticsEngine()
        self.renderer = renderer or TextRenderer()

    def generate_compiler_summary(self, session: CompilerSession) -> str:
        """Generates a structured compiler session report and renders it."""
        summary = self.diagnostics_engine.generate_compiler_summary(session)

        report_data = {
            "title": "Compiler Session Summary",
            "sections": {
                "Overview": {
                    "Compiler Version": summary["version"],
                    "Backend": summary["backend"],
                    "Artifacts Produced": summary["artifact_count"],
                    "Diagnostics Emitted": summary["diagnostics_count"]
                },
                "Hints": summary["hints"]
            }
        }

        return self.renderer.render(report_data)

    def generate_architecture_report(self, session: CompilerSession) -> str:
        """Generates a structured architecture report and renders it."""
        meta = session.compiler_metadata
        flags = session.replay_session.feature_flags

        report_data = {
            "title": "Architecture Report",
            "sections": {
                "Metadata": {
                    "Strict Mode": meta.get("strict_mode", "Unknown"),
                    "Invariant Checks Passed": meta.get("invariants_passed", "Unknown")
                },
                "FeatureFlags": dict(flags)
            }
        }

        return self.renderer.render(report_data)
