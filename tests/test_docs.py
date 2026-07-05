import os
import pytest

DOCS_DIR = "docs"

def test_manual_exists():
    assert os.path.exists(os.path.join(DOCS_DIR, "manual", "index.md"))
    chapters = [
        "repository_overview.md", "architecture_overview.md", "compiler_pipeline.md",
        "runtime_pipeline.md", "backend_architecture.md", "plugin_architecture.md",
        "performance_framework.md", "verification_framework.md", "tooling.md",
        "testing.md", "debugging.md", "diagnostics.md", "repository_layout.md",
        "development_workflow.md", "code_review_expectations.md", "coding_standards.md",
        "contribution_guide.md", "release_process.md"
    ]
    for ch in chapters:
        assert os.path.exists(os.path.join(DOCS_DIR, "manual", ch))

def test_architecture_guides_exist():
    assert os.path.exists(os.path.join(DOCS_DIR, "architecture", "index.md"))
    guides = [
        "capability_resolver.md", "execution_planner.md", "logical_ir.md",
        "lowering.md", "physical_ir.md", "backend_adapter.md", "backend_intelligence.md",
        "runtime.md", "compiler_pipeline.md", "optimization_pipeline.md",
        "verification.md", "performance.md", "tooling.md", "plugin_system.md"
    ]
    for g in guides:
        assert os.path.exists(os.path.join(DOCS_DIR, "architecture", g))

def test_tutorials_exist():
    assert os.path.exists(os.path.join(DOCS_DIR, "tutorials", "index.md"))
    tuts = [
        "add_a_compiler_pass.md", "add_a_backend.md", "create_a_plugin.md",
        "write_a_verification_rule.md", "add_a_tooling_exporter.md",
        "create_a_cli_command.md", "debug_lowering.md", "inspect_physical_ir.md",
        "replay_compiler_sessions.md", "profile_compiler_performance.md",
        "run_verification.md", "write_repository_tests.md"
    ]
    for t in tuts:
        assert os.path.exists(os.path.join(DOCS_DIR, "tutorials", t))

def test_references_exist():
    assert os.path.exists(os.path.join(DOCS_DIR, "reference", "index.md"))
    refs = [
        "compiler_apis.md", "runtime_apis.md", "backend_apis.md",
        "tooling_apis.md", "plugin_apis.md", "verification_apis.md",
        "configuration_apis.md", "cli_commands.md"
    ]
    for r in refs:
        assert os.path.exists(os.path.join(DOCS_DIR, "reference", r))

def test_workflows_exist():
    assert os.path.exists(os.path.join(DOCS_DIR, "workflows", "index.md"))
    wfs = [
        "adding_a_new_model_family.md", "adding_a_backend.md",
        "adding_optimization_passes.md", "adding_verification.md",
        "creating_benchmarks.md", "debugging_compiler_failures.md",
        "debugging_backend_translation.md", "running_stress_tests.md",
        "repository_release_workflow.md"
    ]
    for w in wfs:
        assert os.path.exists(os.path.join(DOCS_DIR, "workflows", w))

def test_examples_exist():
    assert os.path.exists(os.path.join(DOCS_DIR, "examples", "index.md"))
    exs = [
        "minimal_compiler_pipeline.md", "minimal_backend.md",
        "minimal_plugin.md", "minimal_optimization_pass.md",
        "minimal_verification_rule.md", "minimal_tooling_extension.md",
        "minimal_runtime_setup.md"
    ]
    for e in exs:
        assert os.path.exists(os.path.join(DOCS_DIR, "examples", e))

def test_glossary_exists():
    assert os.path.exists(os.path.join(DOCS_DIR, "glossary", "glossary.md"))

def test_reports_exist():
    assert os.path.exists(os.path.join(DOCS_DIR, "audit", "developer_documentation_audit.md"))
    assert os.path.exists(os.path.join(DOCS_DIR, "audit", "documentation_gap_analysis.md"))
    assert os.path.exists(os.path.join(DOCS_DIR, "audit", "documentation_organization_report.md"))
    assert os.path.exists(os.path.join(DOCS_DIR, "reports", "repository_documentation_report.md"))
    assert os.path.exists(os.path.join(DOCS_DIR, "reports", "rollback_procedure.md"))
    assert os.path.exists(os.path.join(DOCS_DIR, "reports", "recommendations_for_docs_003.md"))
    assert os.path.exists(os.path.join(DOCS_DIR, "reports", "documentation_validation_report.md"))
