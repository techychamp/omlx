import json
import pytest

from omlx.registry.base import (
    RegistryEntry,
    GenericRegistry,
    RegistryPhase,
    RegistryLockedError,
    RegistryDuplicateError,
    RegistryDependencyError,
)
from omlx.registry.core import MetadataCapabilityRegistry, MetadataCapabilityEntry

def test_registry_lifecycle():
    reg = MetadataCapabilityRegistry()
    assert reg._phase == RegistryPhase.BUILDING

    entry = MetadataCapabilityEntry(id="test_cap", display_name="Test", description="desc")
    reg.register(entry)

    assert reg.get("test_cap") == entry

    reg.lock()
    assert reg._phase == RegistryPhase.LOCKED

    with pytest.raises(RegistryLockedError):
        reg.register(MetadataCapabilityEntry(id="another", display_name="Another", description="desc"))

def test_duplicate_registration():
    reg = MetadataCapabilityRegistry()
    entry1 = MetadataCapabilityEntry(id="cap1", display_name="Cap 1", description="desc", aliases=["c1"])
    reg.register(entry1)

    # Duplicate ID
    with pytest.raises(RegistryDuplicateError):
        reg.register(MetadataCapabilityEntry(id="cap1", display_name="Cap 1 Again", description="desc"))

    # Duplicate Alias
    with pytest.raises(RegistryDuplicateError):
        reg.register(MetadataCapabilityEntry(id="cap2", display_name="Cap 2", description="desc", aliases=["c1"]))

def test_alias_resolution():
    reg = MetadataCapabilityRegistry()
    entry = MetadataCapabilityEntry(id="cap1", display_name="Cap 1", description="desc", aliases=["alias1", "alias2"])
    reg.register(entry)

    assert reg.get("alias1") == entry
    assert reg.get("alias2") == entry
    assert reg.exists("alias1")

def test_dependency_validation():
    reg = MetadataCapabilityRegistry()
    entry1 = MetadataCapabilityEntry(id="cap1", display_name="Cap 1", description="desc", dependencies=["cap2"])
    reg.register(entry1)

    # Missing dependency
    with pytest.raises(RegistryDependencyError):
        reg.lock()

    reg2 = MetadataCapabilityRegistry()
    entryA = MetadataCapabilityEntry(id="A", display_name="A", description="desc", dependencies=["B"])
    entryB = MetadataCapabilityEntry(id="B", display_name="B", description="desc", dependencies=["A"])
    reg2.register(entryA)
    reg2.register(entryB)

    # Dependency cycle
    with pytest.raises(RegistryDependencyError):
        reg2.lock()

    reg3 = MetadataCapabilityRegistry()
    entryC = MetadataCapabilityEntry(id="C", display_name="C", description="desc")
    entryD = MetadataCapabilityEntry(id="D", display_name="D", description="desc", dependencies=["C"])
    reg3.register(entryC)
    reg3.register(entryD)

    # Valid dependencies
    reg3.lock()

def test_iteration():
    reg = MetadataCapabilityRegistry()
    e1 = MetadataCapabilityEntry(id="1", display_name="1", description="desc")
    e2 = MetadataCapabilityEntry(id="2", display_name="2", description="desc")
    reg.register(e1)
    reg.register(e2)

    entries = list(reg)
    assert len(entries) == 2
    assert e1 in entries
    assert e2 in entries

def test_serialization():
    reg = MetadataCapabilityRegistry()
    entry = MetadataCapabilityEntry(id="cap1", display_name="Cap 1", description="desc", metadata={"key": "value"})
    reg.register(entry)

    json_str = reg.to_json()
    data = json.loads(json_str)

    assert "cap1" in data
    assert data["cap1"]["display_name"] == "Cap 1"
    assert data["cap1"]["metadata"]["key"] == "value"

def test_deserialization():
    json_data = json.dumps({
        "cap1": {
            "id": "cap1",
            "display_name": "Cap 1",
            "description": "Desc",
            "version": "1.0",
            "tags": [],
            "aliases": [],
            "metadata": {},
            "created_by": "system",
            "source": "internal",
            "status": "active",
            "dependencies": []
        }
    })

    reg = MetadataCapabilityRegistry()
    reg.from_json(json_data, MetadataCapabilityEntry)

    entry = reg.get("cap1")
    assert entry is not None
    assert entry.display_name == "Cap 1"

def test_thread_safety():
    # Basic check to ensure threading primitives exist and don't fail
    reg = MetadataCapabilityRegistry()
    reg.lock()
    reg.shutdown()

def test_registry_container():
    from omlx.registry.core import RegistryContainer
    from omlx.registry import RegistryPhase
    container = RegistryContainer()
    assert container.capabilities._phase == RegistryPhase.BUILDING
    
    container.lock_all()
    assert container.capabilities._phase == RegistryPhase.LOCKED
    assert container.backends._phase == RegistryPhase.LOCKED


