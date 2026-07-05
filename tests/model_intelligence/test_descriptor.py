import pytest
from dataclasses import FrozenInstanceError
from typing import Dict, Any

from omlx.framework.model_intelligence.descriptor import ModelDescriptor

def test_model_descriptor_instantiation_and_immutability():
    descriptor = ModelDescriptor(
        model_id="test-model",
        model_family="Autoregressive",
        architecture="Transformer",
        task="Text-Generation",
        modality="Text",
        parameter_count=7000000000,
        hidden_size=4096,
        layer_count=32,
        attention_type="GQA",
        activation_type="silu",
        kv_cache_support=True,
        speculative_support=False,
        streaming_support=True,
        expert_support=False,
        vision_support=False,
        audio_support=False,
        tool_support=False,
        embedding_support=False,
        reranking_support=False,
        quantization_support=True,
        backend_requirements=["mlx"],
        planner_metadata={"foo": "bar"},
        compiler_metadata={"baz": "qux"}
    )

    # Verify values
    assert descriptor.model_id == "test-model"
    assert descriptor.model_family == "Autoregressive"
    assert descriptor.kv_cache_support is True

    # Verify collection types are strictly immutable
    assert isinstance(descriptor.backend_requirements, tuple)

    # Try to modify a field (should fail due to frozen=True)
    with pytest.raises(FrozenInstanceError):
        descriptor.model_id = "new-id"

    # Try to modify planner metadata (should fail due to MappingProxyType)
    with pytest.raises(TypeError):
        descriptor.planner_metadata["foo"] = "new-value"
