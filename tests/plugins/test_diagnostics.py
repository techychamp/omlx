import pytest
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.diagnostics import DiagnosticsGenerator
from omlx.plugins.descriptor import PluginDescriptor, PluginCategory

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
