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

        normalized["tokenizer"] = tokenizer

        return normalized
