import pytest
from unittest.mock import Mock
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.manager import PluginManager
from omlx.plugins.descriptor import PluginLifecycleState

def test_plugin_initialization_failure_recording():
    registry = PluginRegistry()
    manager = PluginManager(registry, runtime_context=None, feature_flags=None)

    class FailingModule:
        @staticmethod
        def get_descriptor():
            from omlx.plugins.descriptor import PluginDescriptor, PluginCategory
            return PluginDescriptor(
                plugin_id="fail.plugin",
                name="Fail",
                version="1.0.0",
                author="Test",
                description="Test",
                category=PluginCategory.CAPABILITY
            )
        @staticmethod
        def initialize_plugin(context):
            raise ValueError("Intentional crash")

    mock_ep = Mock()
    mock_ep.name = "fail_plugin"
    mock_ep.load.return_value = FailingModule
    manager._discovered_entry_points["fail_plugin"] = mock_ep

    manager.load_plugins()
    manager.initialize_plugins()

    assert registry.get_state("fail.plugin") == PluginLifecycleState.FAILED
    assert "initialization_failures" in registry._diagnostics
    failure = registry._diagnostics["initialization_failures"]["fail.plugin"]
    assert failure.plugin_id == "fail.plugin"
    assert failure.exception == "Intentional crash"
