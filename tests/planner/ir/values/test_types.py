import pytest
from types import MappingProxyType
from omlx.planner.ir.values.types import Value, ValueType

def test_value_creation():
    val = Value(id="val1", value_type=ValueType.HIDDEN_STATES, producer_id="node1")
    assert val.id == "val1"
    assert val.value_type == ValueType.HIDDEN_STATES
    assert val.producer_id == "node1"

def test_value_serialization():
    val = Value(id="val1", value_type=ValueType.HIDDEN_STATES, producer_id="node1")
    d = val.to_dict()
    assert d["id"] == "val1"
    assert d["value_type"] == "hidden_states"
    assert d["producer_id"] == "node1"

    val2 = Value.from_dict(d)
    assert val2 == val
