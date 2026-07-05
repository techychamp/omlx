import pytest
import gc
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.sources import RuntimeOverrideSource
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.descriptor import ExecutionFamily

def test_memory_stability():
    resolver = CapabilityResolver()
    planner = ExecutionPlanner()

    gc.collect()
    initial_objects = len(gc.get_objects())

    # Do intense work: parse & plan 5000 times
    for i in range(5000):
        source = RuntimeOverrideSource({
            "execution_family": ExecutionFamily.AUTOREGRESSIVE,
            "execution_hints": {"iteration": str(i)}
        })
        desc = resolver.resolve(additional_sources=[source])
        plan = planner.plan(desc)

    gc.collect()
    final_objects = len(gc.get_objects())

    diff = final_objects - initial_objects
    assert diff < 1000, f"Potential memory leak detected: {diff} new objects left"
