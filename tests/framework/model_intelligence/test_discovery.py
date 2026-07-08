from pathlib import Path
import json

import pytest

from omlx.framework.model_intelligence.discovery import ModelDiscoveryFramework

def test_model_discovery(tmp_path):
    framework = ModelDiscoveryFramework()

    # Create fake model metadata
    model_dir = tmp_path / "test_model"
    model_dir.mkdir()

    config = {
        "architecture": "LlamaForCausalLM",
        "model_type": "llama",
        "num_hidden_layers": 32,
        "num_attention_heads": 32,
        "hidden_size": 4096,
        "quantization_config": {"quant_method": "awq"}
    }
    with open(model_dir / "config.json", "w") as f:
        json.dump(config, f)

    tokenizer_config = {
        "chat_template": "{% if messages[0]['role'] == 'system' %}{{ messages[0]['content'] }}{% endif %}"
    }
    with open(model_dir / "tokenizer_config.json", "w") as f:
        json.dump(tokenizer_config, f)

    descriptor = framework.inspect(model_dir, "test_llama")

    assert descriptor.model_id == "test_llama"
    assert descriptor.model_family == "Autoregressive"
    assert descriptor.architecture == "Transformer"
    assert descriptor.parameter_count == 0  # didn't set in fake metadata
    assert descriptor.hidden_size == 4096
    assert descriptor.layer_count == 32
    assert descriptor.quantization_support is True
