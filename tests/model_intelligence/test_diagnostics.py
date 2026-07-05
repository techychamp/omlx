import pytest
from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.framework.model_intelligence.registry import ModelRegistry
from omlx.framework.model_intelligence.diagnostics import DiagnosticsGenerator
from omlx.framework.model_intelligence.statistics import StatisticsCollector

def test_diagnostics_and_statistics():
    registry = ModelRegistry()
    registry.register(ModelDescriptor(
        model_id="llama-7b",
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
        quantization_support=False,
        backend_requirements=["mlx"],
        planner_metadata={},
        compiler_metadata={}
    ))

    # Diagnostics
    diag = DiagnosticsGenerator(registry)
    summary = diag.generate_model_summary("llama-7b")
    assert summary["model_id"] == "llama-7b"
    assert summary["family"] == "Autoregressive"

    cap_report = diag.generate_capability_report("llama-7b")
    assert cap_report["kv_cache"] is True
    assert cap_report["vision"] is False

    arch_report = diag.generate_architecture_report()
    assert arch_report["total_models"] == 1
    assert arch_report["architectures"]["Transformer"] == 1

    # Statistics
    stats_col = StatisticsCollector(registry)
    stats = stats_col.collect()

    assert stats["total_models"] == 1
    assert stats["family_distribution"]["Autoregressive"] == 1
    assert stats["capability_distribution"]["kv_cache"] == 1
