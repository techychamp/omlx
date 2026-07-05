import pytest
from types import MappingProxyType
from omlx.framework.quantization import (
    QuantizationFamily,
    QuantizationDescriptor,
    QuantizationClassifier,
    QuantizationCapabilityExtractor,
    QuantizationNormalizer,
    QuantizationDiscoveryFramework,
    QuantizationRegistry,
    QuantizationCompatibilityFramework,
    QuantizationCostModel,
    QuantizationDiagnostics,
    QuantizationStatistics
)
from omlx.framework.model_intelligence.descriptor import ModelDescriptor

def test_descriptor_immutability():
    desc = QuantizationDescriptor(
        quantization_family=QuantizationFamily.INT4,
        storage_precision="int4",
        compute_precision="fp16",
        weight_precision="int4",
        activation_precision="fp16",
        kv_cache_precision="fp16",
        group_size=128,
        block_size=None,
        mixed_precision=False,
        dynamic_quantization=False,
        static_quantization=True,
        per_channel=False,
        per_group=True,
        supports_streaming=True,
        supports_batching=True,
        supports_speculative_decoding=False,
        supported_backends=("mlx", "cuda"),
        supported_model_families=("llama",),
        metadata=MappingProxyType({"dummy": True}),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({}),
        backend_metadata=MappingProxyType({})
    )

    with pytest.raises(Exception): # dataclass frozen check
        desc.group_size = 64

    assert isinstance(desc.supported_backends, tuple)
    assert isinstance(desc.metadata, MappingProxyType)

def test_classifier():
    classifier = QuantizationClassifier()

    # MLX
    assert classifier.classify_mlx({"quantization": {"bits": 4}}) == QuantizationFamily.INT4
    assert classifier.classify_mlx({"quantization": {"bits": 8}}) == QuantizationFamily.INT8
    assert classifier.classify_mlx({"quantization": {}}) == QuantizationFamily.MLX

    # GGUF
    assert classifier.classify_gguf({"general.file_type": 2}) == QuantizationFamily.INT4
    assert classifier.classify_gguf({"general.file_type": 3}) == QuantizationFamily.INT8
    assert classifier.classify_gguf({"some_key": "is_gguf_format"}) == QuantizationFamily.GGUF

    # HF
    assert classifier.classify_hf({"quantization_config": {"quant_method": "awq"}}) == QuantizationFamily.AWQ
    assert classifier.classify_hf({"quantization_config": {"quant_method": "gptq"}}) == QuantizationFamily.GPTQ

def test_discovery():
    discovery = QuantizationDiscoveryFramework()

    desc = discovery.discover_from_hf({"quantization_config": {"quant_method": "awq", "group_size": 64}})
    assert desc.quantization_family == QuantizationFamily.AWQ
    assert desc.weight_precision == "int4"
    assert desc.group_size == 64

def test_registry():
    desc1 = QuantizationDescriptor(
        quantization_family=QuantizationFamily.INT4,
        storage_precision="int4",
        compute_precision="fp16",
        weight_precision="int4",
        activation_precision="fp16",
        kv_cache_precision="fp16",
        group_size=128,
        block_size=None,
        mixed_precision=False,
        dynamic_quantization=False,
        static_quantization=True,
        per_channel=False,
        per_group=True,
        supports_streaming=True,
        supports_batching=True,
        supports_speculative_decoding=False,
        supported_backends=("mlx",),
        supported_model_families=("llama",),
        metadata=MappingProxyType({}),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({}),
        backend_metadata=MappingProxyType({})
    )
    desc2 = QuantizationDescriptor(
        quantization_family=QuantizationFamily.INT8,
        storage_precision="int8",
        compute_precision="fp16",
        weight_precision="int8",
        activation_precision="fp16",
        kv_cache_precision="fp16",
        group_size=None,
        block_size=None,
        mixed_precision=False,
        dynamic_quantization=False,
        static_quantization=True,
        per_channel=False,
        per_group=False,
        supports_streaming=True,
        supports_batching=True,
        supports_speculative_decoding=False,
        supported_backends=("cuda",),
        supported_model_families=("mistral",),
        metadata=MappingProxyType({}),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({}),
        backend_metadata=MappingProxyType({})
    )

    registry = QuantizationRegistry([desc1, desc2])

    assert len(registry.get_all()) == 2
    assert len(registry.query_by_family(QuantizationFamily.INT4)) == 1
    assert len(registry.query_by_precision("int8")) == 1
    assert len(registry.query_by_backend_compatibility("mlx")) == 1
    assert len(registry.query_by_model_family("llama")) == 1

def test_compatibility():
    compat = QuantizationCompatibilityFramework()

    quant_desc = QuantizationDescriptor(
        quantization_family=QuantizationFamily.INT4,
        storage_precision="int4",
        compute_precision="fp16",
        weight_precision="int4",
        activation_precision="fp16",
        kv_cache_precision="fp16",
        group_size=128,
        block_size=None,
        mixed_precision=False,
        dynamic_quantization=False,
        static_quantization=True,
        per_channel=False,
        per_group=True,
        supports_streaming=True,
        supports_batching=True,
        supports_speculative_decoding=False,
        supported_backends=("mlx",),
        supported_model_families=("llama",),
        metadata=MappingProxyType({}),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({}),
        backend_metadata=MappingProxyType({})
    )

    model_desc = ModelDescriptor(
        model_id="test",
        model_family="llama",
        architecture="llama",
        task="text-generation",
        modality="text",
        parameter_count=7_000_000_000,
        hidden_size=4096,
        layer_count=32,
        attention_type="sdpa",
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
        backend_requirements=(),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({})
    )

    class DummyBackend:
        backend_id = "mlx"

    backend = DummyBackend()

    assert compat.evaluate_model_compatibility(quant_desc, model_desc)
    assert compat.evaluate_backend_compatibility(quant_desc, backend)

def test_cost_model():
    cost = QuantizationCostModel()

    quant_desc = QuantizationDescriptor(
        quantization_family=QuantizationFamily.INT4,
        storage_precision="int4",
        compute_precision="fp16",
        weight_precision="int4",
        activation_precision="fp16",
        kv_cache_precision="fp16",
        group_size=128,
        block_size=None,
        mixed_precision=False,
        dynamic_quantization=False,
        static_quantization=True,
        per_channel=False,
        per_group=True,
        supports_streaming=True,
        supports_batching=True,
        supports_speculative_decoding=False,
        supported_backends=("mlx",),
        supported_model_families=("llama",),
        metadata=MappingProxyType({}),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({}),
        backend_metadata=MappingProxyType({})
    )

    model_desc = ModelDescriptor(
        model_id="test",
        model_family="llama",
        architecture="llama",
        task="text-generation",
        modality="text",
        parameter_count=7_000_000_000,
        hidden_size=4096,
        layer_count=32,
        attention_type="sdpa",
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
        backend_requirements=(),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({})
    )

    mem = cost.estimate_memory_usage(quant_desc, model_desc)
    assert mem == int(7_000_000_000 * 0.5)

def test_diagnostics_and_statistics():
    desc = QuantizationDescriptor(
        quantization_family=QuantizationFamily.INT4,
        storage_precision="int4",
        compute_precision="fp16",
        weight_precision="int4",
        activation_precision="fp16",
        kv_cache_precision="fp16",
        group_size=128,
        block_size=None,
        mixed_precision=False,
        dynamic_quantization=False,
        static_quantization=True,
        per_channel=False,
        per_group=True,
        supports_streaming=True,
        supports_batching=True,
        supports_speculative_decoding=False,
        supported_backends=("mlx",),
        supported_model_families=("llama",),
        metadata=MappingProxyType({}),
        planner_metadata=MappingProxyType({}),
        compiler_metadata=MappingProxyType({}),
        backend_metadata=MappingProxyType({})
    )

    diag = QuantizationDiagnostics()
    summary = diag.generate_summary(desc)
    assert summary["family"] == QuantizationFamily.INT4.value

    stats = QuantizationStatistics()
    res = stats.aggregate([desc, desc])
    assert res["total_count"] == 2
    assert res["family_distribution"][QuantizationFamily.INT4.value] == 2
