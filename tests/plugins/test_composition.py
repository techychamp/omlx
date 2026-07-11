import pytest
from unittest.mock import Mock
from omlx.plugins.contracts import ExtensionPoint
from omlx.plugins.descriptor import PluginDescriptor, PluginCategory, PluginPriority, PluginCapability
from omlx.plugins.registry import PluginRegistry
from omlx.plugins.orchestrator import ExtensionOrchestrator

class MockExtension(ExtensionPoint):
    def __init__(self, id_val, owner, capabilities):
        self._id = id_val
        self._owner = owner
        self._caps = capabilities

    @property
    def extension_id(self): return self._id

    @property
    def plugin_owner(self): return self._owner

    @property
    def capabilities(self): return self._caps

def test_priority_ordering():
    registry = PluginRegistry()
    orchestrator = ExtensionOrchestrator(registry)

    # Register plugins with different priorities
    desc1 = PluginDescriptor("p1", "P1", "1", "A", "D", PluginCategory.CAPABILITY, priority=PluginPriority.STANDARD)
    desc2 = PluginDescriptor("p2", "P2", "1", "A", "D", PluginCategory.CAPABILITY, priority=PluginPriority.CORE)
    desc3 = PluginDescriptor("p3", "P3", "1", "A", "D", PluginCategory.CAPABILITY, priority=PluginPriority.EXPERIMENTAL)

    registry.register_plugin(desc1)
    registry.register_plugin(desc2)
    registry.register_plugin(desc3)

    ext1 = MockExtension("e1", "p1", [])
    ext2 = MockExtension("e2", "p2", [])
    ext3 = MockExtension("e3", "p3", [])
    ext_no_plugin = MockExtension("e_unknown", "unknown_plugin", [])

    # Shuffle list
    extensions = [ext3, ext1, ext2, ext_no_plugin]

    # CORE (0) < STANDARD (3) < EXPERIMENTAL (5)
    ordered = orchestrator.order_extensions(extensions, ExtensionPoint)

    # ext2 (CORE) -> ext1 (STANDARD) -> ext_no_plugin (STANDARD default) -> ext3 (EXPERIMENTAL)
    assert ordered[0].extension_id == "e2"
    assert ordered[1].extension_id == "e1"
    assert ordered[2].extension_id == "e_unknown"
    assert ordered[3].extension_id == "e3"

def test_grouping():
    registry = PluginRegistry()
    orchestrator = ExtensionOrchestrator(registry)

    ext1 = MockExtension("e1", "p1", [PluginCapability.COMPILER_EXTENSION])
    ext2 = MockExtension("e2", "p2", [PluginCapability.COMPILER_EXTENSION, PluginCapability.PLANNER_EXTENSION])

    grouped = orchestrator.group_extensions_by_capability([ext1, ext2])

    assert len(grouped[PluginCapability.COMPILER_EXTENSION.value]) == 2
    assert len(grouped[PluginCapability.PLANNER_EXTENSION.value]) == 1

def test_conflict_detection():
    registry = PluginRegistry()
    orchestrator = ExtensionOrchestrator(registry)

    ext1 = MockExtension("dup_id", "p1", [])
    ext2 = MockExtension("dup_id", "p2", [])

    conflicts = orchestrator.detect_conflicts([ext1, ext2])
    assert len(conflicts) == 1
    assert "Duplicate extension ID detected: dup_id" in conflicts[0]
