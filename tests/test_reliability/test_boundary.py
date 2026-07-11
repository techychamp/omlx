import pytest
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.sources import RuntimeOverrideSource
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.descriptor import ExecutionFamily

def test_empty_metadata_boundary():
    resolver = CapabilityResolver()
    # Call with strictly minimal empty metadata
    source = RuntimeOverrideSource({})
    desc = resolver.resolve(additional_sources=[source])
    # The system should fall back to defaults
    assert desc.execution_family == ExecutionFamily.AUTOREGRESSIVE

def test_large_capability_sets():
    resolver = CapabilityResolver()
    large_set = {f"cap_{i}": True for i in range(10000)}
    # The resolver filters kwargs down to what is allowed by the descriptor
    source = RuntimeOverrideSource(large_set)
    desc = resolver.resolve(additional_sources=[source])
    assert desc is not None

def test_large_execution_hints():
    resolver = CapabilityResolver()
    hints = {f"hint_{i}": "A" * 100 for i in range(10000)}
    source = RuntimeOverrideSource({"execution_hints": hints})
    desc = resolver.resolve(additional_sources=[source])

    planner = ExecutionPlanner()
    plan = planner.plan(desc).execution_plan
    # Validate the plan correctly encapsulated all huge hints
    assert len(plan.execution_hints) == 10000
