import pytest
from unittest.mock import Mock
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.manager import PluginManager
from omlx.plugins.descriptor import PluginLifecycleState

def test_plugin_manager_lifecycle():
    registry = PluginRegistry()
    manager = PluginManager(registry, runtime_context=None, feature_flags=None)

    # Mock entry points discovery
    mock_ep = Mock()
    mock_ep.name = "example_plugin"

    # Define a mock module
    class MockModule:
        @staticmethod
        def get_descriptor():
            from omlx.plugins.descriptor import PluginDescriptor, PluginCategory
            return PluginDescriptor(
                plugin_id="mock.plugin",
                name="Mock Plugin",
                version="1.0.0",
                author="Test",
                description="Test",
                category=PluginCategory.CAPABILITY
            )
        @staticmethod
        def initialize_plugin(context):
            pass

    mock_ep.load.return_value = MockModule

    # Manually inject the mock entry point for testing
    manager._discovered_entry_points["example_plugin"] = mock_ep

    # Test loading
    manager.load_plugins()
    assert "mock.plugin" in manager._loaded_modules
    assert registry.get_state("mock.plugin") == PluginLifecycleState.LOADED

    # Test initialization
    manager.initialize_plugins()
    assert registry.get_state("mock.plugin") == PluginLifecycleState.INITIALIZED

    # Test validation and sealing
    manager.validate_and_seal()
    assert registry.get_state("mock.plugin") == PluginLifecycleState.ENABLED
    assert registry._is_sealed == True
