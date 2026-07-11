import pytest
from omlx.runtime.builder import RuntimeBuilder, RuntimeStateEnum
from omlx.runtime.feature_flags import FeatureFlags

def test_runtime_builder_creation():
    builder = RuntimeBuilder()
    runtime = builder.build()

    assert runtime is not None
    assert runtime.state == RuntimeStateEnum.BOOTSTRAPPING
    assert runtime.context is not None
    assert isinstance(runtime.context.feature_flags, FeatureFlags)

def test_lifecycle_transitions():
    builder = RuntimeBuilder()
    runtime = builder.build()

    runtime.transition(RuntimeStateEnum.INITIALIZING)
    assert runtime.state == RuntimeStateEnum.INITIALIZING

    runtime.transition(RuntimeStateEnum.READY)
    assert runtime.state == RuntimeStateEnum.READY

def test_dependency_ownership():
    mock_pool = object()
    mock_settings = object()
    mock_verification = object()

    builder = RuntimeBuilder()
    builder.with_engine_pool(mock_pool)
    builder.with_settings(mock_settings)
    builder.with_verification(mock_verification)

    runtime = builder.build()

    assert runtime.engine_pool is mock_pool
    assert runtime.settings is mock_settings
    assert runtime.verification_framework is mock_verification
    assert runtime.context.settings is mock_settings

def test_context_immutability():
    builder = RuntimeBuilder()
    runtime = builder.build()

    with pytest.raises(Exception): # Assuming dataclasses.FrozenInstanceError
        runtime.context.settings = object()

def test_double_initialization():
    pass # Add logic later
