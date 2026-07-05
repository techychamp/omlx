import pytest
from omlx.framework.model_intelligence.normalizer import MetadataNormalizer

def test_normalization():
    normalizer = MetadataNormalizer()

    # Test flat HF config style
    raw = {
        "config": {
            "model_type": "llama",
            "hidden_size": 4096,
            "num_hidden_layers": 32,
            "num_attention_heads": 32,
            "hidden_act": "silu"
        },
        "tokenizer": {"chat_template": "x"}
    }

    normalized = normalizer.normalize(raw)
    assert normalized["model_type"] == "llama"
    assert normalized["hidden_size"] == 4096
    assert normalized["num_hidden_layers"] == 32
    assert normalized["num_attention_heads"] == 32
    assert normalized["hidden_act"] == "silu"
    assert "chat_template" in normalized["tokenizer"]

    # Test generic dict style with alternative keys
    raw2 = {
        "config": {
            "model_type": "custom",
            "d_model": 2048,
            "n_layers": 16,
            "n_heads": 16,
            "activation_function": "gelu"
        }
    }

    normalized2 = normalizer.normalize(raw2)
    assert normalized2["hidden_size"] == 2048
    assert normalized2["num_hidden_layers"] == 16
    assert normalized2["num_attention_heads"] == 16
    assert normalized2["hidden_act"] == "gelu"
