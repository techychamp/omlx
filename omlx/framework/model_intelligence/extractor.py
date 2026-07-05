# SPDX-License-Identifier: Apache-2.0
"""
Capability Extraction Logic.

Infers model capabilities based on metadata.
"""

from typing import Dict, Any

class CapabilityExtractor:
    """
    Extracts capabilities strictly from metadata without loading weights.
    """
    def extract(self, normalized_config: Dict[str, Any], arch: str, family: str) -> Dict[str, Any]:
        caps = {
            "kv_cache_support": False,
            "speculative_support": False,
            "streaming_support": False,
            "expert_support": False,
            "vision_support": False,
            "audio_support": False,
            "tool_support": False,
            "embedding_support": False,
            "reranking_support": False,
            "quantization_support": False,
            "attention_type": "Standard",
            "backend_requirements": ["mlx"]
        }

        model_type = normalized_config.get("model_type", "").lower()

        # KV Cache & Streaming are common for autoregressive text generation
        if family == "Autoregressive" or family == "Vision-Language" or family == "Audio":
            caps["kv_cache_support"] = True
            caps["streaming_support"] = True

        # Attention Type
        num_kv_heads = normalized_config.get("num_key_value_heads", normalized_config.get("num_attention_heads", 0))
        num_heads = normalized_config.get("num_attention_heads", 0)

        if num_kv_heads > 0 and num_heads > 0:
            if num_kv_heads == 1:
                caps["attention_type"] = "MQA"
            elif num_kv_heads < num_heads:
                caps["attention_type"] = "GQA"

        # MoE Support
        if family == "Mixture of Experts":
            caps["expert_support"] = True

        # Modality Specifics
        if family == "Vision-Language":
            caps["vision_support"] = True
        if family == "Audio":
            caps["audio_support"] = True

        # Tool Calling (heuristics based on chat templates or specific models)
        if "chat_template" in normalized_config.get("tokenizer", {}):
            template = str(normalized_config["tokenizer"]["chat_template"]).lower()
            if "tool" in template or "function" in template:
                caps["tool_support"] = True

        # Embeddings & Reranking
        if "embedding" in model_type:
            caps["embedding_support"] = True
        if "rerank" in model_type:
            caps["reranking_support"] = True

        # Quantization
        if "quantization_config" in normalized_config:
            caps["quantization_support"] = True

        return caps
