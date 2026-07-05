import pytest
from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.framework.model_intelligence.registry import ModelRegistry

def create_mock_descriptor(model_id: str, family: str, arch: str, caps: dict) -> ModelDescriptor:
    return ModelDescriptor(
        model_id=model_id,
        model_family=family,
        architecture=arch,
        task="Test",
        modality="Text",
        parameter_count=100,
        hidden_size=10,
        layer_count=2,
        attention_type="MQA",
        activation_type="silu",
        kv_cache_support=caps.get("kv", False),
        speculative_support=False,
        streaming_support=False,
        expert_support=caps.get("moe", False),
        vision_support=caps.get("vision", False),
        audio_support=False,
        tool_support=False,
        embedding_support=False,
        reranking_support=False,
        quantization_support=False,
        backend_requirements=["mlx"],
        planner_metadata={},
        compiler_metadata={}
    )


def test_registry():
    registry = ModelRegistry()

    # Register models
    d1 = create_mock_descriptor("llama-7b", "Autoregressive", "Transformer", {"kv": True})
    d2 = create_mock_descriptor("mixtral", "Mixture of Experts", "Transformer", {"kv": True, "moe": True})
    d3 = create_mock_descriptor("llava", "Vision-Language", "Transformer", {"kv": True, "vision": True})

    registry.register(d1)
    registry.register(d2)
    registry.register(d3)

    # Query tests
    assert len(registry.get_all()) == 3
    assert registry.get("llama-7b") == d1

    assert len(registry.query_by_family("Autoregressive")) == 1
    assert len(registry.query_by_family("Vision-Language")) == 1

    assert len(registry.query_by_architecture("Transformer")) == 3
    assert len(registry.query_by_architecture("UNet")) == 0

    assert len(registry.query_by_capability("kv_cache")) == 3
    assert len(registry.query_by_capability("vision")) == 1
    assert len(registry.query_by_capability("expert")) == 1

    # Freeze test
    registry.freeze()

    with pytest.raises(RuntimeError):
        registry.register(create_mock_descriptor("new-model", "Family", "Arch", {}))
