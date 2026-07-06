import pytest
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily, CacheLayoutType, AttentionType
from omlx.planner.planner import ExecutionPlanner
from omlx.planner.compatibility import ExecutionProfileAdapter
from omlx.inference.execution_profile import ExecutionProfile

def test_execution_profile_adapter_direct_mapping():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        supported_modalities=("text",),
        attention_types=(AttentionType.CAUSAL,),
        cache_layout=CacheLayoutType.PAGED,
        supports_streaming=True,
        supports_speculative=False,
        execution_hints={
             "attention_mode": "custom_causal",
             "sampler_mode": "custom_sampler",
             "position_encoding": "custom_rope",
             "version": "v2"
        }
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor).execution_plan

    profile = ExecutionProfileAdapter.adapt(plan)

    assert isinstance(profile, ExecutionProfile)
    assert profile.backend_name == "autoregressive"
    assert profile.cache_mode == "standard"
    assert profile.streaming_mode == "streaming"
    assert profile.attention_mode == "custom_causal"
    assert profile.sampler_mode == "custom_sampler"
    assert profile.position_encoding == "custom_rope"
    assert profile.version == "v2"

def test_execution_profile_adapter_defaults():
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        supports_streaming=False,
        cache_layout=CacheLayoutType.NONE
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor).execution_plan

    profile = ExecutionProfileAdapter.adapt(plan)

    assert profile.backend_name == "autoregressive"
    assert profile.streaming_mode == "standard"

    # Asserting that the dataclass defaults are used since hints were omitted
    assert profile.attention_mode == "causal"
    assert profile.sampler_mode == "standard"
    assert profile.position_encoding == "rope"
    assert profile.version == "v1"
