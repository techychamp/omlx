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

def test_deep_immutability():
    resolver = CapabilityResolver()
    source = RuntimeOverrideSource({
        "execution_hints": {"nested": [1, 2, 3], "nested_dict": {"a": 1}},
        "supported_modalities": ["text", "image"]
    })
    descriptor = resolver.resolve(additional_sources=[source])

    assert isinstance(descriptor.execution_hints, __import__('types').MappingProxyType)
    assert isinstance(descriptor.execution_hints["nested"], tuple)
    assert isinstance(descriptor.execution_hints["nested_dict"], __import__('types').MappingProxyType)
    assert isinstance(descriptor.supported_modalities, tuple)

    with pytest.raises(TypeError):
        descriptor.execution_hints["new_key"] = "value"

    with pytest.raises(TypeError):
        descriptor.execution_hints["nested"][0] = 5

def test_merge_provenance():
    resolver = CapabilityResolver()
    source1 = ModelMetadataSource({"model_type": "stable_diffusion"})
    source2 = RuntimeOverrideSource({"execution_family": ExecutionFamily.AUTOREGRESSIVE, "attention_types": [AttentionType.CAUSAL]})

    descriptor = resolver.resolve(additional_sources=[source1, source2])

    assert descriptor._diagnostics is not None
    prov = descriptor._diagnostics["execution_family"]
    assert prov.value == ExecutionFamily.AUTOREGRESSIVE
    assert prov.winner == "RuntimeOverrideSource"
    assert prov.history == ["ModelMetadataSource", "RuntimeOverrideSource"]

    prov_attention = descriptor._diagnostics["attention_types"]
    assert prov_attention.value == [AttentionType.CAUSAL]
    assert prov_attention.winner == "RuntimeOverrideSource"
    assert prov_attention.history == ["ModelMetadataSource", "RuntimeOverrideSource"]

from omlx.capabilities.validation import ValidationRule

class DummyRule(ValidationRule):
    def validate(self, caps):
        if caps.get("supports_verification", False):
            raise CapabilityValidationError("Dummy rule failed")

def test_extensible_validation():
    resolver = CapabilityResolver(validation_rules=[DummyRule()])
    source = RuntimeOverrideSource({"supports_verification": True})

    with pytest.raises(CapabilityValidationError, match="Dummy rule failed"):
        resolver.resolve(additional_sources=[source])

import concurrent.futures

def test_thread_safety():
    resolver = CapabilityResolver()
    source1 = ModelMetadataSource({"model_type": "stable_diffusion"})
    source2 = ModelMetadataSource({"model_type": "llama"})
    source3 = RuntimeOverrideSource({"supports_streaming": True})

    def resolve_diff():
        return resolver.resolve(additional_sources=[source1])

    def resolve_auto():
        return resolver.resolve(additional_sources=[source2, source3])

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for _ in range(50):
            futures.append(executor.submit(resolve_diff))
            futures.append(executor.submit(resolve_auto))

        for idx, f in enumerate(futures):
            desc = f.result()
            if idx % 2 == 0:
                assert desc.execution_family == ExecutionFamily.DIFFUSION
                assert desc.supports_streaming is False
            else:
                assert desc.execution_family == ExecutionFamily.AUTOREGRESSIVE
                assert desc.supports_streaming is True
