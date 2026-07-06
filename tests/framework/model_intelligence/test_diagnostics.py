from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.framework.model_intelligence.registry import ModelRegistry
from omlx.framework.model_intelligence.diagnostics import DiagnosticsGenerator

def test_diagnostics():
    registry = ModelRegistry()
    descriptor = ModelDescriptor(
        model_id="test_model",
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
        tool_support=True,
        embedding_support=False,
        reranking_support=False,
        quantization_support=False,
        backend_requirements=("mlx",),
        planner_metadata={},
        compiler_metadata={},
        architecture_family="Transformer",
        architecture_generation="Unknown",
        context_length=0,
        tokenizer_family="Unknown",
        special_token_information={},
        moe_information={},
        expert_count=0,
        expert_size=0,
        license="Unknown",
        repository_metadata={},
        recommended_backend="Unknown",
        recommended_quantization="Unknown",
        recommended_execution_mode="Unknown",
        recommended_scheduler="Unknown",
        compatibility_report={},
        validation_report={}
    )
    registry.register(descriptor)
    generator = DiagnosticsGenerator(registry)

    summary = generator.generate_model_summary("test_model")
    assert summary["model_id"] == "test_model"
    assert summary["family"] == "Autoregressive"

    caps = generator.generate_capability_report("test_model")
    assert caps["kv_cache"] is True
    assert caps["streaming"] is True

    archs = generator.generate_architecture_report()
    assert archs["total_models"] == 1
    assert archs["architectures"]["Transformer"] == 1

    disco = generator.generate_discovery_report()
    assert disco["total_discovered"] == 1
    assert "Autoregressive" in disco["families"]
