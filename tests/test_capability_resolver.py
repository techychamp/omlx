import pytest
from omlx.capabilities import (
    CapabilityResolver,
    ModelMetadataSource,
    RuntimeOverrideSource,
    ExecutionFamily,
    AttentionType,
    CacheLayoutType,
    CapabilityValidationError
)

def test_resolve_default():
    resolver = CapabilityResolver()
    descriptor = resolver.resolve()
    assert descriptor.execution_family == ExecutionFamily.AUTOREGRESSIVE
    assert descriptor.supports_streaming is True
    assert descriptor.cache_layout == CacheLayoutType.PAGED

def test_resolve_model_metadata_autoregressive():
    resolver = CapabilityResolver()
    source = ModelMetadataSource({"model_type": "llama"})
    descriptor = resolver.resolve(additional_sources=[source])
    assert descriptor.execution_family == ExecutionFamily.AUTOREGRESSIVE

def test_resolve_model_metadata_diffusion():
    resolver = CapabilityResolver()
    source = ModelMetadataSource({"model_type": "stable_diffusion"})
    descriptor = resolver.resolve(additional_sources=[source])
    assert descriptor.execution_family == ExecutionFamily.DIFFUSION
    assert AttentionType.DIFFUSION in descriptor.attention_types
    assert descriptor.supports_diffusion is True
    assert descriptor.supports_streaming is False

def test_resolve_model_metadata_embedding():
    resolver = CapabilityResolver()
    source = ModelMetadataSource({"model_type": "nomic_embedding"})
    descriptor = resolver.resolve(additional_sources=[source])
    assert descriptor.execution_family == ExecutionFamily.EMBEDDING
    assert AttentionType.BIDIRECTIONAL in descriptor.attention_types
    assert descriptor.supports_embedding is True
    assert descriptor.supports_streaming is False

def test_merge_precedence():
    resolver = CapabilityResolver()
    source1 = ModelMetadataSource({"model_type": "stable_diffusion"})
    # Override should take precedence if ordered correctly (ascending precedence in list)
    source2 = RuntimeOverrideSource({"execution_family": ExecutionFamily.AUTOREGRESSIVE, "attention_types": [AttentionType.CAUSAL]})

    descriptor = resolver.resolve(additional_sources=[source1, source2])
    assert descriptor.execution_family == ExecutionFamily.AUTOREGRESSIVE

def test_validation_failure():
    resolver = CapabilityResolver()
    source = RuntimeOverrideSource({
        "execution_family": ExecutionFamily.DIFFUSION,
        "supports_streaming": True
    })

    with pytest.raises(CapabilityValidationError, match="Diffusion models do not support streaming"):
        resolver.resolve(additional_sources=[source])

def test_validation_failure_attention():
    resolver = CapabilityResolver()
    source = RuntimeOverrideSource({
        "execution_family": ExecutionFamily.DIFFUSION,
        "attention_types": [AttentionType.CAUSAL]
    })

    with pytest.raises(CapabilityValidationError, match="Diffusion models cannot use causal attention"):
        resolver.resolve(additional_sources=[source])
