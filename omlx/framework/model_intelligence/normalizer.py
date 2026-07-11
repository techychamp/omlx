# SPDX-License-Identifier: Apache-2.0
"""
Metadata Normalization.

Normalizes metadata from Hugging Face, MLX, and other formats into a canonical dictionary.
"""

from typing import Dict, Any

class MetadataNormalizer:
    """
    Normalizes diverse config formats into a canonical representation.
    """
    def normalize(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        config = raw_metadata.get("config", {})
        tokenizer = raw_metadata.get("tokenizer", {})
        generation = raw_metadata.get("generation", {})
        tokenizer_json = raw_metadata.get("tokenizer_json", {})
        special_tokens_map = raw_metadata.get("special_tokens_map", {})

        normalized: Dict[str, Any] = {}

        # Merge dictionaries (with config having primary importance)
        for d in [tokenizer, generation, config]:
            if isinstance(d, dict):
                 for k, v in d.items():
                     normalized[k] = v

        # Normalize specific fields
        # Hidden Size
        if "hidden_size" not in normalized and "d_model" in normalized:
            normalized["hidden_size"] = normalized["d_model"]

        # Layers
        if "num_hidden_layers" not in normalized and "n_layers" in normalized:
             normalized["num_hidden_layers"] = normalized["n_layers"]

        # Heads
        if "num_attention_heads" not in normalized and "n_heads" in normalized:
             normalized["num_attention_heads"] = normalized["n_heads"]

        # Activation
        if "hidden_act" not in normalized and "activation_function" in normalized:
            normalized["hidden_act"] = normalized["activation_function"]

        # Context length
        context_keys = ["max_position_embeddings", "max_seq_len", "max_seq_length", "seq_length", "n_positions"]
        for key in context_keys:
            if key in config:
                normalized["context_length"] = config[key]
                break
        if "context_length" not in normalized:
            if "model_max_length" in tokenizer:
                normalized["context_length"] = tokenizer["model_max_length"]
            else:
                normalized["context_length"] = 2048 # Fallback

        normalized["tokenizer"] = tokenizer
        normalized["tokenizer_json"] = tokenizer_json
        normalized["special_tokens_map"] = special_tokens_map

        # Pass through other metadata
        normalized["readme"] = raw_metadata.get("readme", "")
        normalized["safetensors_metadata"] = raw_metadata.get("safetensors_metadata", {})
        normalized["gguf_metadata"] = raw_metadata.get("gguf_metadata", {})
        normalized["mlx_metadata"] = raw_metadata.get("mlx_metadata", {})

        return normalized
