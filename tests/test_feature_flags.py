import pytest
import os
from omlx.feature_flags.models import FeatureFlag, FlagLifecycle, FlagCategory, FlagType
from omlx.feature_flags.system import FeatureFlagSystem

@pytest.fixture
def ff_system():
    return FeatureFlagSystem()

def test_register_and_default_resolution(ff_system):
    ff_system.register(FeatureFlag(
        name="test_flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    snapshot = ff_system.take_snapshot()
    assert snapshot.is_enabled("test_flag") is False
    assert snapshot.get("test_flag") is False

def test_env_var_override(ff_system, monkeypatch):
    ff_system.register(FeatureFlag(
        name="test_flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001",
        env_var_name="MY_CUSTOM_ENV"
    ))

    monkeypatch.setenv("MY_CUSTOM_ENV", "true")
    snapshot = ff_system.take_snapshot()
    assert snapshot.is_enabled("test_flag") is True

def test_default_env_var_name(ff_system, monkeypatch):
    ff_system.register(FeatureFlag(
        name="my-cool-flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    monkeypatch.setenv("OMLX_FF_MY_COOL_FLAG", "1")
    snapshot = ff_system.take_snapshot()
    assert snapshot.is_enabled("my-cool-flag") is True

def test_config_override(ff_system):
    ff_system.register(FeatureFlag(
        name="test_flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    ff_system.set_config_overrides({"test_flag": True})
    snapshot = ff_system.take_snapshot()
    assert snapshot.is_enabled("test_flag") is True

def test_cli_override(ff_system):
    ff_system.register(FeatureFlag(
        name="test_flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    ff_system.set_config_overrides({"test_flag": False})
    ff_system.set_cli_overrides({"test_flag": True}) # CLI should win over config
    snapshot = ff_system.take_snapshot()
    assert snapshot.is_enabled("test_flag") is True

def test_precedence(ff_system, monkeypatch):
    ff_system.register(FeatureFlag(
        name="test_flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    monkeypatch.setenv("OMLX_FF_TEST_FLAG", "1") # ENV overrides config
    ff_system.set_config_overrides({"test_flag": False})

    snapshot = ff_system.take_snapshot()
    assert snapshot.is_enabled("test_flag") is True

def test_immutability(ff_system):
    ff_system.register(FeatureFlag(
        name="test_flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    ff_system.take_snapshot()

    with pytest.raises(RuntimeError):
        ff_system.register(FeatureFlag(
            name="late_flag",
            description="too late",
            category=FlagCategory.EXPERIMENTAL,
            lifecycle=FlagLifecycle.EXPERIMENTAL,
            default_value=False,
            owner="test",
            creation_checkpoint="IMP-001"
        ))

    with pytest.raises(RuntimeError):
        ff_system.set_config_overrides({"test_flag": True})

    with pytest.raises(RuntimeError):
        ff_system.set_cli_overrides({"test_flag": True})

def test_invalid_flag_detection(ff_system):
    ff_system.take_snapshot()
    snapshot = ff_system.snapshot()

    with pytest.raises(ValueError):
        snapshot.get("unknown_flag")

def test_duplicate_registration(ff_system):
    ff_system.register(FeatureFlag(
        name="test_flag",
        description="A test flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    with pytest.raises(ValueError):
        ff_system.register(FeatureFlag(
            name="test_flag",
            description="Duplicate",
            category=FlagCategory.EXPERIMENTAL,
            lifecycle=FlagLifecycle.EXPERIMENTAL,
            default_value=True,
            owner="test",
            creation_checkpoint="IMP-001"
        ))

def test_type_resolution(ff_system, monkeypatch):
    ff_system.register(FeatureFlag(
        name="int_flag",
        description="A test int flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        flag_type=FlagType.INTEGER,
        default_value=10,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    monkeypatch.setenv("OMLX_FF_INT_FLAG", "42")
    snapshot = ff_system.take_snapshot()
    assert snapshot.get("int_flag") == 42

def test_export_and_list(ff_system):
    ff_system.register(FeatureFlag(
        name="flag1",
        description="First flag",
        category=FlagCategory.EXPERIMENTAL,
        lifecycle=FlagLifecycle.EXPERIMENTAL,
        default_value=True,
        owner="test",
        creation_checkpoint="IMP-001"
    ))
    ff_system.register(FeatureFlag(
        name="flag2",
        description="Second flag",
        category=FlagCategory.RUNTIME,
        lifecycle=FlagLifecycle.PRIMARY,
        default_value=False,
        owner="test",
        creation_checkpoint="IMP-001"
    ))

    snapshot = ff_system.take_snapshot()
    exported = snapshot.export()
    assert exported == {"flag1": True, "flag2": False}

    flags = snapshot.list()
    assert len(flags) == 2

    runtime_flags = snapshot.get_flags_by_category(FlagCategory.RUNTIME)
    assert len(runtime_flags) == 1
    assert runtime_flags[0].name == "flag2"
