# SPDX-License-Identifier: Apache-2.0

import pytest
from omlx.tooling.framework.unified import get_tooling
from omlx.api.v1.runtime import RuntimeBuilder

def test_unified_tooling_registry():
    tooling = get_tooling()
    assert tooling.get_inspector("compiler") is not None
    assert tooling.get_inspector("runtime") is not None
    assert tooling.get_inspector("execution") is not None
    assert tooling.get_inspector("backend") is not None

    assert tooling.get_validator("default") is not None
    assert tooling.get_profiler("default") is not None
    assert tooling.get_benchmark("default") is not None

def test_runtime_inspector():
    tooling = get_tooling()
    runtime = RuntimeBuilder().configure({"test": "value"}).build()

    inspector = tooling.get_inspector("runtime")
    config = inspector.inspect_configuration(runtime)

    assert "state" in config

def test_snapshot_manager():
    tooling = get_tooling()
    runtime = RuntimeBuilder().build()

    snapshot = tooling.snapshot_manager.create_snapshot(runtime)
    assert "configuration" in snapshot.data

def test_validation_helper():
    tooling = get_tooling()
    validator = tooling.get_validator("default")
    from omlx.api.v1.runtime import RuntimeConfig

    config = RuntimeConfig(settings={"a": 1})
    report = validator.validate_runtime_config(config)
    assert report.is_valid

def test_diagnostics_framework():
    from omlx.tooling.diagnostics.diagnostic_framework import DiagnosticFramework
    framework = DiagnosticFramework()

    runtime_report = framework.get_runtime_diagnostics()
    assert runtime_report.subsystem == "runtime"

    compiler_report = framework.get_compiler_diagnostics()
    assert compiler_report.subsystem == "compiler"

def test_plugin_manager():
    from omlx.tooling.plugins.plugin_manager import ToolingPluginManager
    manager = ToolingPluginManager()

    class CustomInspector:
        def inspect(self): return "custom"

    manager.register_custom_inspector("my_custom", CustomInspector())

    tooling = get_tooling()
    custom = tooling.get_inspector("my_custom")
    assert custom is not None
    assert custom.inspect() == "custom"
