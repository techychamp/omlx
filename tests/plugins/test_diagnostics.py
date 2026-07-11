import pytest
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.diagnostics import DiagnosticsGenerator, PluginDiagnosticsGenerator
from omlx.plugins.descriptor import PluginDescriptor, PluginCategory
from omlx.plugins.graph import PluginDependencyGraph
from omlx.plugins.lifecycle import PluginLifecycleMonitor

def test_diagnostics_generation():
    registry = PluginRegistry()
    desc = PluginDescriptor("test", "T", "1", "A", "D", PluginCategory.CAPABILITY)
    registry.register_plugin(desc)

    gen = DiagnosticsGenerator(registry)

    report = gen.generate_full_report()

    assert "composition" in report
    assert "configurations" in report
    assert "priorities" in report
    assert "extensions" in report

    assert report["configurations"]["test"]["enabled"] == True
    assert report["priorities"]["test"] == "STANDARD"

def test_plugin_diagnostics_generator():
    registry = PluginRegistry()
    desc = PluginDescriptor("test", "T", "1", "A", "D", PluginCategory.CAPABILITY)
    registry.register_plugin(desc)

    graph = PluginDependencyGraph(nodes={}, roots=frozenset())
    monitor = PluginLifecycleMonitor()

    gen = PluginDiagnosticsGenerator(registry, graph, monitor)
    report = gen.generate()

    assert "dependency_graph_report" in report
    assert "trust_report" in report
    assert "permission_report" in report
    assert "lifecycle_report" in report
    assert "registry_report" in report
    assert "sandbox_report" in report
