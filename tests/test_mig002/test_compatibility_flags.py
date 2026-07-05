import pytest
import os
from unittest.mock import patch, MagicMock

# We'll use mocked imports or a separate file if mlx breaks imports,
# but let's just test the profile registry behavior first.

def test_feature_flags_exist():
    from omlx.runtime.feature_flags import FeatureFlags
    flags = FeatureFlags()
    assert hasattr(flags, "EXECUTION_PLAN_RUNTIME_ENABLED")
    assert hasattr(flags, "EXECUTION_PROFILE_COMPATIBILITY_ENABLED")
    assert hasattr(flags, "EXECUTION_PLAN_VALIDATION_ENABLED")
