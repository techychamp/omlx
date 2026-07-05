import pytest
from omlx.plugins.descriptor import PluginDescriptor, PluginCategory
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.compatibility import CompatibilityNegotiator

def test_version_compatibility():
    registry = PluginRegistry()
    negotiator = CompatibilityNegotiator(registry, "2.0.0", "1.5.0")

    desc_ok = PluginDescriptor(
        "p_ok", "OK", "1", "A", "D", PluginCategory.CAPABILITY,
        supported_compiler_versions=(">=2.0.0",),
        supported_runtime_versions=(">=1.5.0",)
    )

    desc_fail_compiler = PluginDescriptor(
        "p_c", "C", "1", "A", "D", PluginCategory.CAPABILITY,
        supported_compiler_versions=("==1.0.0",)
    )

    desc_fail_runtime = PluginDescriptor(
        "p_r", "R", "1", "A", "D", PluginCategory.CAPABILITY,
        supported_runtime_versions=(">=2.0.0",)
    )

    desc_duplicate = PluginDescriptor(
        "p_ok", "Dup", "1", "A", "D", PluginCategory.CAPABILITY
    )

    diagnostics = negotiator.check_compatibility([desc_ok, desc_fail_compiler, desc_fail_runtime, desc_duplicate])

    assert len(diagnostics["version_conflicts"]) == 3 # duplicate + p_c + p_r

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
    assert "requires p2 2.0.0, but v1.0.0 is installed" in diagnostics["dependency_conflicts"][0]

from omlx.plugins.descriptor import PluginTrustLevel

def test_conflict_resolution():
    registry = PluginRegistry()

    # Competing Implementations
    desc1 = PluginDescriptor(
        "p1", "P1", "1.0", "A", "D", PluginCategory.CAPABILITY,
        provided_extension_points=("ext_a",)
    )
    desc2 = PluginDescriptor(
        "p2", "P2", "1.0", "A", "D", PluginCategory.CAPABILITY,
        provided_extension_points=("ext_a",)
    )

    # Trust conflict
    desc_core = PluginDescriptor(
        "p_core", "Core", "1.0", "A", "D", PluginCategory.CAPABILITY,
        trust_level=PluginTrustLevel.CORE,
        dependencies={"p_untrusted": "1.0"}
    )
    desc_untrusted = PluginDescriptor(
        "p_untrusted", "Untrusted", "1.0", "A", "D", PluginCategory.CAPABILITY,
        trust_level=PluginTrustLevel.UNTRUSTED
    )

    registry.register_plugin(desc1)
    registry.register_plugin(desc2)
    registry.register_plugin(desc_core)
    registry.register_plugin(desc_untrusted)

    negotiator = CompatibilityNegotiator(registry, "1.0", "1.0")
    diagnostics = negotiator.check_compatibility([desc1, desc2, desc_core, desc_untrusted])

    assert len(diagnostics["competing_implementations"]) == 1
    assert "ext_a provided by both p1 and p2" in diagnostics["competing_implementations"][0]

    assert len(diagnostics["trust_conflicts"]) == 1
    assert "Trusted plugin p_core depends on untrusted plugin p_untrusted" in diagnostics["trust_conflicts"][0]
