import pytest
from omlx.plugins.descriptor import PluginDescriptor, PluginCategory
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.compatibility import CompatibilityNegotiator

def test_version_compatibility():
    registry = PluginRegistry()
    negotiator = CompatibilityNegotiator(registry, "2.0.0", "1.5.0")

    desc_ok = PluginDescriptor(
        "p_ok", "OK", "1", "A", "D", PluginCategory.CAPABILITY,
        supported_compiler_versions=("2.0.0",),
        supported_runtime_versions=("1.5.0",)
    )

    desc_fail_compiler = PluginDescriptor(
        "p_c", "C", "1", "A", "D", PluginCategory.CAPABILITY,
        supported_compiler_versions=("1.0.0",)
    )

    desc_fail_runtime = PluginDescriptor(
        "p_r", "R", "1", "A", "D", PluginCategory.CAPABILITY,
        supported_runtime_versions=("2.0.0",)
    )

    desc_duplicate = PluginDescriptor(
        "p_ok", "Dup", "1", "A", "D", PluginCategory.CAPABILITY
    )

    diagnostics = negotiator.check_compatibility([desc_ok, desc_fail_compiler, desc_fail_runtime, desc_duplicate])

    assert len(diagnostics["version_conflicts"]) == 3

def test_dependency_compatibility():
    registry = PluginRegistry()

    # p1 requires p2 v2.0
    desc1 = PluginDescriptor(
        "p1", "P1", "1", "A", "D", PluginCategory.CAPABILITY,
        dependencies={"p2": "2.0.0"}
    )

    # but p2 v1.0 is installed
    desc2 = PluginDescriptor("p2", "P2", "1.0.0", "A", "D", PluginCategory.CAPABILITY)

    registry.register_plugin(desc1)
    registry.register_plugin(desc2)

    negotiator = CompatibilityNegotiator(registry, "1.0", "1.0")
    diagnostics = negotiator.check_compatibility([desc1, desc2])

    assert len(diagnostics["dependency_conflicts"]) == 1
    assert "requires p2 v2.0.0, but v1.0.0 is installed" in diagnostics["dependency_conflicts"][0]
