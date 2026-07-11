import pytest
import tempfile
import json
from pathlib import Path
from omlx.framework.model_intelligence.discovery import ModelDiscoveryFramework

def test_discovery_framework():
    with tempfile.TemporaryDirectory() as tmpdir:
        model_dir = Path(tmpdir) / "test-model"
        model_dir.mkdir()

        # Write mock config
        config = {
            "model_type": "llama",
            "num_hidden_layers": 32,
            "hidden_size": 4096,
            "num_attention_heads": 32,
            "num_key_value_heads": 8,
            "hidden_act": "silu"
        }
        with open(model_dir / "config.json", "w") as f:
            json.dump(config, f)

        # Write mock tokenizer config
        tokenizer_config = {
            "chat_template": "{% for message in messages %}{{ message['role'] + ': ' + message['content'] + '\n' }}{% endfor %}"
        }
        with open(model_dir / "tokenizer_config.json", "w") as f:
            json.dump(tokenizer_config, f)

        framework = ModelDiscoveryFramework()
        descriptor = framework.inspect(model_dir, "test-model")

        assert descriptor.model_id == "test-model"
        assert descriptor.model_family == "Autoregressive"
        assert descriptor.architecture == "Transformer"
        assert descriptor.layer_count == 32
        assert descriptor.hidden_size == 4096
        assert descriptor.attention_type == "GQA"
        assert descriptor.activation_type == "silu"
        assert descriptor.kv_cache_support is True
        assert descriptor.tool_support is False # No tool mentioned in template
