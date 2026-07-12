import pytest
from omlx.compiler.registry.core import Registry

def test_registry_registration():
    reg = Registry("test")

    @reg.register("item1")
    class Item1:
        pass

    assert reg.has("item1")
    assert reg.get("item1") is Item1

def test_registry_duplicate_registration_fails():
    reg = Registry("test")

    @reg.register("item1")
    class Item1:
        pass

    with pytest.raises(ValueError):
        @reg.register("item1")
        class Item2:
            pass

def test_registry_missing_item_fails():
    reg = Registry("test")
    with pytest.raises(KeyError):
        reg.get("missing")

def test_registry_direct_registration():
    reg = Registry("test")
    class Item1:
        pass

    reg.register("item1", Item1)

    assert reg.has("item1")
    assert reg.get("item1") is Item1
