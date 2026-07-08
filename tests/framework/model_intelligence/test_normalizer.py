from omlx.framework.model_intelligence.normalizer import MetadataNormalizer

def test_normalizer():
    normalizer = MetadataNormalizer()

    # Test normalization of typical keys
    raw_metadata = {
        "config": {
            "d_model": 4096,
            "n_layers": 32,
            "n_heads": 32,
            "activation_function": "silu"
        },
        "tokenizer": {
            "bos_token": "<s>"
        }
    }

    normalized = normalizer.normalize(raw_metadata)

    assert normalized["hidden_size"] == 4096
    assert normalized["num_hidden_layers"] == 32
    assert normalized["num_attention_heads"] == 32
    assert normalized["hidden_act"] == "silu"
    assert normalized["tokenizer"] == {"bos_token": "<s>"}
