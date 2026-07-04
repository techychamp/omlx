import pytest
from unittest.mock import Mock, patch

from omlx.plugins.descriptor import PluginDescriptor, PluginCategory, PluginLifecycleState
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.manager import PluginManager

class MockPluginModule:
    def __init__(self, plugin_id):
        self.descriptor = PluginDescriptor(
            plugin_id=plugin_id, name="Test", version="1.0", author="A", description="D", category=PluginCategory.CAPABILITY
        )

    def get_descriptor(self):
        return self.descriptor

    def initialize_plugin(self, context):
        context.add_diagnostic("initialized", True)

def test_plugin_manager_initialization():
    registry = PluginRegistry()
    pm = PluginManager(registry=registry, runtime_context={}, feature_flags={})
    assert pm.registry is not None

@patch('importlib.metadata.entry_points')
def test_plugin_manager_lifecycle(mock_entry_points):
    # Mock entry points
    mock_ep = Mock()
    mock_ep.name = "test_plugin"
    mock_ep.load.return_value = MockPluginModule("plugin.test")

    # Python 3.10+ entry_points behavior
    mock_eps = Mock()
    mock_eps.select.return_value = [mock_ep]
    mock_entry_points.return_value = mock_eps

    registry = PluginRegistry()
    pm = PluginManager(registry=registry, runtime_context={}, feature_flags={})

    # Discovery phase
    pm.discover_plugins()
    assert "test_plugin" in pm._discovered_entry_points
    assert pm.registry.get_descriptor("plugin.test") is None # Not loaded yet

    # Load phase
    pm.load_plugins()
    assert pm.registry.get_descriptor("plugin.test") is not None
    assert pm.registry.get_state("plugin.test") == PluginLifecycleState.LOADED

    # Initialization phase
    pm.initialize_plugins()
    assert pm.registry.get_state("plugin.test") == PluginLifecycleState.INITIALIZED

def test_plugin_manager_validation_and_seal():
    registry = PluginRegistry()
    pm = PluginManager(registry=registry, runtime_context={}, feature_flags={})

    # Manual registration for test
    desc = PluginDescriptor(
        plugin_id="plugin.a", name="A", version="1.0", author="A", description="D", category=PluginCategory.CAPABILITY
    )
    pm.registry.register_plugin(desc)
    pm._loaded_modules["plugin.a"] = MockPluginModule("plugin.a") # Mock it being loaded

    pm.validate_and_seal()

    assert pm.registry.get_state("plugin.a") == PluginLifecycleState.ENABLED

    with pytest.raises(RuntimeError):
        pm.registry.register_plugin(desc)
