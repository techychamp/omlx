import pytest
import threading
from types import MappingProxyType

from omlx.plugins.descriptor import PluginDescriptor, PluginCategory, PluginLifecycleState
from omlx.plugins.context import PluginInitializationContext
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.contracts import BackendPlugin

def test_plugin_descriptor_immutability():
    descriptor = PluginDescriptor(
        plugin_id="com.omlx.test_plugin",
        name="Test Plugin",
        version="1.0.0",
        author="OMLX Team",
        description="A test plugin",
        category=PluginCategory.BACKEND,
        dependencies={"plugin.b": "1.0"},
        supported_compiler_versions=["v1", "v2"]
    )

    # Check top-level immutability
    with pytest.raises(Exception):
        descriptor.name = "Modified Plugin"

    # Check deep immutability
    assert isinstance(descriptor.dependencies, MappingProxyType)
    assert isinstance(descriptor.supported_compiler_versions, tuple)

    with pytest.raises(TypeError):
        descriptor.dependencies["plugin.c"] = "2.0"

    with pytest.raises(AttributeError):
        descriptor.supported_compiler_versions.append("v3")

def test_plugin_registration():
    registry = PluginRegistry()
    descriptor = PluginDescriptor(
        plugin_id="com.omlx.test",
        name="Test",
        version="1.0",
        author="Author",
        description="Desc",
        category=PluginCategory.CAPABILITY
    )

    registry.register_plugin(descriptor)

    assert registry.get_descriptor("com.omlx.test") == descriptor
    assert registry.get_state("com.omlx.test") == PluginLifecycleState.REGISTERED

def test_duplicate_registration_fails():
    registry = PluginRegistry()
    descriptor = PluginDescriptor(
        plugin_id="com.omlx.test",
        name="Test",
        version="1.0",
        author="Author",
        description="Desc",
        category=PluginCategory.CAPABILITY
    )

    registry.register_plugin(descriptor)

    with pytest.raises(ValueError):
        registry.register_plugin(descriptor)

def test_registry_sealing():
    registry = PluginRegistry()
    descriptor = PluginDescriptor(
        plugin_id="com.omlx.test",
        name="Test",
        version="1.0",
        author="Author",
        description="Desc",
        category=PluginCategory.CAPABILITY
    )

    registry.seal()

    with pytest.raises(RuntimeError):
        registry.register_plugin(descriptor)

    with pytest.raises(RuntimeError):
        registry.transition_state("com.omlx.test", PluginLifecycleState.LOADED)

def test_dependency_validation():
    registry = PluginRegistry()

    # Plugin A depends on Plugin B
    desc_a = PluginDescriptor(
        plugin_id="plugin.a", name="A", version="1.0", author="A", description="A",
        category=PluginCategory.CAPABILITY,
        dependencies={"plugin.b": "1.0"}
    )

    registry.register_plugin(desc_a)
    registry.validate_dependencies()

    assert registry.get_state("plugin.a") == PluginLifecycleState.FAILED

    diagnostics = registry.generate_diagnostics_report()
    assert "Missing required dependency: plugin.b" in diagnostics["dependency"]["plugin.a"]

def test_circular_dependency():
    registry = PluginRegistry()

    # Plugin A depends on B
    desc_a = PluginDescriptor(
        plugin_id="plugin.a", name="A", version="1.0", author="A", description="A", category=PluginCategory.CAPABILITY,
        dependencies={"plugin.b": "1.0"}
    )

    # Plugin B depends on A
    desc_b = PluginDescriptor(
        plugin_id="plugin.b", name="B", version="1.0", author="B", description="B", category=PluginCategory.CAPABILITY,
        dependencies={"plugin.a": "1.0"}
    )

    registry.register_plugin(desc_a)
    registry.register_plugin(desc_b)

    registry.validate_dependencies()

    assert registry.get_state("plugin.a") == PluginLifecycleState.FAILED

    diagnostics = registry.generate_diagnostics_report()
    assert "Circular dependency detected" in diagnostics["dependency"]["global"]

class MockBackendExtension(BackendPlugin):
    @property
    def extension_id(self) -> str:
        return "mock_backend"

def test_extension_lookup():
    registry = PluginRegistry()
    descriptor = PluginDescriptor(
        plugin_id="plugin.a", name="A", version="1.0", author="A", description="A", category=PluginCategory.BACKEND
    )

    ext = MockBackendExtension()
    registry.register_plugin(descriptor)
    registry.register_extensions("plugin.a", [ext])

    extensions = registry.get_extensions(BackendPlugin)
    assert len(extensions) == 1
    assert extensions[0] == ext

def test_thread_safety():
    registry = PluginRegistry()

    def register_worker(i):
        desc = PluginDescriptor(
            plugin_id=f"plugin.{i}", name=f"P{i}", version="1.0", author="A", description="D", category=PluginCategory.CAPABILITY
        )
        registry.register_plugin(desc)
        registry.transition_state(f"plugin.{i}", PluginLifecycleState.LOADED)

    threads = []
    for i in range(100):
        t = threading.Thread(target=register_worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    for i in range(100):
        assert registry.get_state(f"plugin.{i}") == PluginLifecycleState.LOADED
