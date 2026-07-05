# SPDX-License-Identifier: Apache-2.0
"""Test Migration Verification mapping legacy execution profiles to execution plans."""

import pytest
from types import MappingProxyType
from omlx.inference.execution_profile import get_profile_registry, ExecutionContext, RuntimeConfiguration
from omlx.registry.model_info import ModelInfo
from omlx.runtime.capabilities import EngineCapabilities, ModelCapabilities
from omlx.runtime.feature_flags import FeatureFlags
from omlx.planner.planner import ExecutionPlanner
from omlx.capabilities.descriptor import CapabilityDescriptor, ExecutionFamily, CacheLayoutType, AttentionType

def test_migration_legacy_vs_compiler():
    """Compare a legacy execution profile resolution against compiler planning."""

    # Mock legacy context dependencies
    model_capabilities = ModelCapabilities()
    model_info = ModelInfo(
        model_path="mock/path",
        architecture="LlamaForCausalLM",
        config_model_type="llama",
        capabilities=model_capabilities,
        generation_modes=[],
        preferred_generation_mode="autoregressive",
        cache_type="kv",
        attention_modes=[],
        supports_streaming=True,
        tokenizer_info={}
    )
    capabilities = EngineCapabilities()
    feature_flags = FeatureFlags()

    # Mock legacy context
    context = ExecutionContext(
        model_info=model_info,
        engine_capabilities=capabilities,
        feature_flags=feature_flags,
        runtime_config=RuntimeConfiguration()
    )

    registry = get_profile_registry()
    profile, factory = registry.resolve(context)

    # Mock equivalent CapabilityDescriptor for new compiler
    descriptor = CapabilityDescriptor(
        execution_family=ExecutionFamily.AUTOREGRESSIVE,
        supports_speculative=False,
        supports_streaming=True,
        supports_verification=False,
        cache_layout=CacheLayoutType.PAGED,
        attention_types=(AttentionType.CAUSAL,),
        hardware_requirements=tuple(),
        execution_hints=MappingProxyType({})
    )

    planner = ExecutionPlanner()
    plan = planner.plan(descriptor)

    # Assert equivalence mappings between legacy Profile and new Plan
    assert profile.backend_name == plan.execution_backend
    assert plan.execution_mode == "streaming" # Because supports_streaming is True in descriptor
