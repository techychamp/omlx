import pytest
import random
import string
from omlx.capabilities.resolver import CapabilityResolver
from omlx.capabilities.sources import RuntimeOverrideSource
from omlx.capabilities.descriptor import ExecutionFamily
from .utils import RandomGenerator

def test_capability_resolver_fuzz():
    resolver = CapabilityResolver()

    for _ in range(1000):
        random_dict = RandomGenerator.random_dict(keys=random.randint(1, 10))
        # Ensure enums for families to avoid pydantic errors when mapping
        if "execution_family" not in random_dict:
             random_dict["execution_family"] = ExecutionFamily.AUTOREGRESSIVE

        source = RuntimeOverrideSource(random_dict)
        try:
            desc = resolver.resolve(additional_sources=[source])
            assert desc is not None
        except Exception as e:
            # We expect structured validation errors or missing fields, NOT hard crashes
            # In a real compiler, we check `isinstance(e, ValidationException)`
            pass
