from omlx.framework.model_intelligence.extractor import CapabilityExtractor

def test_extractor():
    extractor = CapabilityExtractor()

    # Text Generation model
    normalized_config = {
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_key_value_heads": 8,
        "tokenizer": {
            "chat_template": "tool_call"
        }
    }
    caps = extractor.extract(normalized_config, "Transformer", "Autoregressive")

    assert caps["kv_cache_support"] is True
    assert caps["streaming_support"] is True
    assert caps["attention_type"] == "GQA"
    assert caps["tool_support"] is True

    # Vision model
    normalized_config = {
        "model_type": "llava",
        "num_attention_heads": 32,
        "num_key_value_heads": 32,
    }
    caps = extractor.extract(normalized_config, "Transformer", "Vision-Language")

    assert caps["vision_support"] is True
    assert caps["attention_type"] == "Standard" # MHA because heads == kv_heads
    assert caps["tool_support"] is False

    # Audio model
    caps = extractor.extract({"model_type": "whisper"}, "Transformer", "Audio")
    assert caps["audio_support"] is True

    # MoE model
    caps = extractor.extract({"model_type": "mixtral", "num_experts": 8}, "Transformer", "Mixture of Experts")
    assert caps["expert_support"] is True

    # Quantization
    caps = extractor.extract({"model_type": "llama", "quantization_config": {"quant_method": "awq"}}, "Transformer", "Autoregressive")
    assert caps["quantization_support"] is True
