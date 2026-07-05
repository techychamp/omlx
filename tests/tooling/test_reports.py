import pytest
import json
from types import MappingProxyType
from omlx.tooling.session.compiler_session import CompilerSession
from omlx.tooling.session.replay_session import ReplaySession
from omlx.tooling.reports.reporter import ReportingEngine, TextRenderer, JsonRenderer, MarkdownRenderer

def test_reporting_engine_renderers():
    replay = ReplaySession(
        compiler_version="1.5",
        planner_version="1.0",
        feature_flags=MappingProxyType({"OMLX_FF_TEST": True}),
        backend="mlx",
        optimization_pipeline=(),
        timestamps=MappingProxyType({})
    )

    session = CompilerSession(
        replay_session=replay,
        artifacts=MappingProxyType({"Plan": {}}),
        compiler_metadata=MappingProxyType({"strict_mode": True, "invariants_passed": True})
    )

    # Text Renderer
    text_reporter = ReportingEngine(renderer=TextRenderer())
    summary_text = text_reporter.generate_compiler_summary(session)
    assert "Overview:" in summary_text
    assert "Compiler Version: 1.5" in summary_text

    arch_text = text_reporter.generate_architecture_report(session)
    assert "Strict Mode: True" in arch_text
    assert "OMLX_FF_TEST: True" in arch_text

    # JSON Renderer
    json_reporter = ReportingEngine(renderer=JsonRenderer())
    summary_json = json_reporter.generate_compiler_summary(session)
    summary_dict = json.loads(summary_json)
    assert summary_dict["title"] == "Compiler Session Summary"
    assert summary_dict["sections"]["Overview"]["Compiler Version"] == "1.5"

    # Markdown Renderer
    md_reporter = ReportingEngine(renderer=MarkdownRenderer())
    summary_md = md_reporter.generate_compiler_summary(session)
    assert "# Compiler Session Summary" in summary_md
    assert "## Overview" in summary_md
    assert "- **Compiler Version**: 1.5" in summary_md
