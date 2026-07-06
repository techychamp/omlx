import pytest
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.sources import RuntimeOverrideSource
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.descriptor import ExecutionFamily
from .utils import GoldenComparator

def test_capability_resolver_determinism():
    resolver = CapabilityResolver()
    source = RuntimeOverrideSource({
        "execution_family": ExecutionFamily.AUTOREGRESSIVE,
        "execution_hints": {"key": "value"}
    })

    # Run multiple times to ensure the exact same outputs
    desc_1 = resolver.resolve(additional_sources=[source])
    desc_2 = resolver.resolve(additional_sources=[source])

    # Ensure immutability and equality across resolution runs
    assert desc_1 == desc_2
    assert id(desc_1) != id(desc_2) # They must be distinct objects, but equal value

def test_planner_determinism():
    resolver = CapabilityResolver()
    planner = ExecutionPlanner()
    source = RuntimeOverrideSource({
        "execution_family": ExecutionFamily.AUTOREGRESSIVE,
        "execution_hints": {"key": "value"}
    })
    desc = resolver.resolve(additional_sources=[source])

    plan_1 = planner.plan(desc).execution_plan
    plan_2 = planner.plan(desc).execution_plan

    # They shouldn't be identically the same object (though if we cache they might be)
    assert id(plan_1) != id(plan_2)

    # But they must equal each other
    # Pydantic / Dataclass usually implements equality. Let's explicitly compare dict representations.
    # Exclude metadata like timing
    p1_dict = dict(plan_1.__dict__)
    p2_dict = dict(plan_2.__dict__)
    p1_dict.pop("planner_metadata", None)
    p2_dict.pop("planner_metadata", None)

    assert p1_dict == p2_dict
