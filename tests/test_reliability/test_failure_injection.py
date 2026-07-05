import pytest
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily
from omlx.planner.planner import ExecutionPlanner
from .utils import FailureInjector

def test_capability_resolver_failure_injection():
    resolver = CapabilityResolver()

    # Inject a realistic failure on a critical path (e.g. internal rule execution)
    original_validate = resolver.validation_engine.validate

    def failing_validate(*args, **kwargs):
        raise ValueError("Simulated Validation Error")

    resolver.validation_engine.validate = failing_validate

    with pytest.raises(ValueError, match="Simulated Validation Error"):
        resolver.resolve()

def test_planner_failure_injection():
    planner = ExecutionPlanner()

    # Suppose one of the passes fails
    class FailingPass:
        name = "FailingPass"
        def apply(self, plan_dict, desc):
            raise RuntimeError("Pass optimization failed")

    planner._pass_registry.get_passes = lambda: [FailingPass()]

    from omlx.capabilities.descriptor import ExecutionFamily
    # Need a mock descriptor
    class MockDesc:
        execution_family = ExecutionFamily.AUTOREGRESSIVE
        cache_layout = "paged"
        supports_streaming = True
        supports_verification = False
        execution_hints = {}
        hardware_requirements = ()
        supports_speculative = False

    with pytest.raises(RuntimeError, match="Pass optimization failed"):
        planner.plan(MockDesc())
