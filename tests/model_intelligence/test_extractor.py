import pytest
from omlx.framework.model_intelligence.extractor import CapabilityExtractor

def test_capability_extraction():
    extractor = CapabilityExtractor()

    # Test Llama GQA
    config = {
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_key_value_heads": 8
    }
    caps = extractor.extract(config, "Transformer", "Autoregressive")
    assert caps["kv_cache_support"] is True
    assert caps["streaming_support"] is True
    assert caps["attention_type"] == "GQA"
    assert caps["vision_support"] is False

    # Test Llama MQA
    config = {
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_key_value_heads": 1
    }
    caps = extractor.extract(config, "Transformer", "Autoregressive")
    assert caps["attention_type"] == "MQA"

    # Test Tool Support via tokenizer
    config = {
        "model_type": "llama",
        "num_attention_heads": 32,
        "num_key_value_heads": 8,
        "tokenizer": {
            "chat_template": "You are a helpful assistant with access to tools."
        }
    }
    caps = extractor.extract(config, "Transformer", "Autoregressive")
    assert caps["tool_support"] is True

    # Test Vision
    config = {"model_type": "llava"}
    caps = extractor.extract(config, "Transformer", "Vision-Language")
    assert caps["vision_support"] is True
    assert caps["kv_cache_support"] is True

    # Test Embedding
    config = {"model_type": "bert-embedding"}
    caps = extractor.extract(config, "Encoder", "Embedding")
    assert caps["embedding_support"] is True
