import pytest
from omlx.plugins.descriptor import PluginDescriptor, PluginCapability, PluginPermission, PluginTrustLevel
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.resolver import PluginDependencyResolver
from omlx.plugins.extensions import PluginRegistryExtensions
from omlx.plugins.lifecycle import PluginLifecycleMonitor
from omlx.plugins.descriptor import PluginLifecycleState
from omlx.plugins.sandbox import PluginSandboxPolicy, SandboxIsolationLevel

def get_test_descriptor(plugin_id, dependencies=None, capabilities=None, permissions=None):
    return PluginDescriptor(
        plugin_id=plugin_id,
        version="1.0.0",
        name=plugin_id,
        author="test",
        description="test",
        category="test",
        dependencies=dependencies or {},
        capabilities=capabilities or tuple(),
        permissions=permissions or tuple()
    )

def test_dependency_resolution():
    registry = PluginRegistry()
    desc_a = get_test_descriptor(plugin_id="plugin_a")
    desc_b = get_test_descriptor(plugin_id="plugin_b", dependencies={"plugin_a": "1.0.0"})
    desc_c = get_test_descriptor(plugin_id="plugin_c", dependencies={"plugin_b": "1.0.0"})

    registry.register_plugin(desc_a)
    registry.register_plugin(desc_b)
    registry.register_plugin(desc_c)

    resolver = PluginDependencyResolver(registry._descriptors)
    graph = resolver.resolve()

    assert "plugin_a" in graph.roots
    assert "plugin_b" not in graph.roots
    assert "plugin_c" not in graph.roots

    assert "plugin_b" in graph.nodes["plugin_a"].required_by
    assert "plugin_c" in graph.nodes["plugin_b"].required_by

    order = graph.get_initialization_order()
    assert order == ["plugin_a", "plugin_b", "plugin_c"]

def test_registry_extensions():
    registry = PluginRegistry()
    desc = get_test_descriptor(
        plugin_id="test",
        capabilities=(PluginCapability.COMPILER_EXTENSION.value,),
        permissions=(PluginPermission.COMPILER_ACCESS,)
    )
    registry.register_plugin(desc)

    exts = PluginRegistryExtensions(registry)

    # We pass the string value for capabilities since they are stored as strings in Descriptor
    assert len(exts.get_by_capability(PluginCapability.COMPILER_EXTENSION.value)) == 1
    assert len(exts.get_by_permission(PluginPermission.COMPILER_ACCESS)) == 1

def test_lifecycle_monitor():
    monitor = PluginLifecycleMonitor()
    monitor.record_transition("test", PluginLifecycleState.REGISTERED)
    monitor.record_transition("test", PluginLifecycleState.LOADED)

    history = monitor.get_history("test")
    assert len(history) == 2
    assert history[0] == PluginLifecycleState.REGISTERED
    assert history[1] == PluginLifecycleState.LOADED

    stats = monitor.get_statistics()
    assert stats["REGISTERED"] == 1
    assert stats["LOADED"] == 1
    assert stats["FAILED"] == 0

def test_sandbox_policy():
    policy = PluginSandboxPolicy(isolation_level=SandboxIsolationLevel.READ_ONLY, thread_safe=False)
    assert policy.isolation_level == SandboxIsolationLevel.READ_ONLY
    assert policy.thread_safe == False
