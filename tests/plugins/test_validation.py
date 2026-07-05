import pytest
from omlx.plugins.descriptor import PluginDescriptor, PluginCategory, PluginTrustLevel, PluginIsolationPolicy
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.validation import PluginValidationFramework

def test_plugin_validation():
    registry = PluginRegistry()
    validator = PluginValidationFramework(registry)

    # Valid plugin
    desc_valid = PluginDescriptor(
        "p_valid", "Valid", "1.0", "A", "D", PluginCategory.CAPABILITY,
        trust_level=PluginTrustLevel.CORE
    )

    # Invalid: Untrusted but allows shared state
    desc_invalid_untrusted = PluginDescriptor(
        "p_untrusted", "Untrusted", "1.0", "A", "D", PluginCategory.CAPABILITY,
        trust_level=PluginTrustLevel.UNTRUSTED,
        isolation_policy=PluginIsolationPolicy(shared_state_allowed=True)
    )

    results = validator.validate_all([desc_valid, desc_invalid_untrusted])

    assert results["p_valid"]["is_valid"] is True
    assert results["p_untrusted"]["is_valid"] is False
    assert "Untrusted/Experimental plugins cannot allow shared state" in results["p_untrusted"]["errors"]
