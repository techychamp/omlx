# SPDX-License-Identifier: Apache-2.0
"""
Model Family Classification.

Classifies models into families, architectures, and tasks based on normalized metadata.
"""

from typing import Dict, Any, Tuple

class ModelClassifier:
    """
    Classifies models deterministically.
    """
    def __init__(self):
        pass

    def classify_architecture(self, config: Dict[str, Any]) -> str:
        """
        Detects the underlying architecture.
        """
        arch = config.get("architecture", config.get("model_type", "Unknown"))
        if "Whisper" in str(config.get("architectures", [])):
            return "Whisper"

        if "Whisper" in str(config.get("architectures", [])):
            return "Whisper"

        if isinstance(arch, list) and arch:
            arch = arch[0]

        arch_lower = str(arch).lower()
        if "llama" in arch_lower or "qwen" in arch_lower or "mistral" in arch_lower or "mixtral" in arch_lower:
            return "Transformer"
        elif "bert" in arch_lower or "roberta" in arch_lower:
            return "Transformer"
        elif "unet" in arch_lower:
            return "UNet"
        elif "dit" in arch_lower:
            return "DiT"
        elif "whisper" in arch_lower:
            return "Whisper"
        elif "mamba" in arch_lower or "ssm" in arch_lower:
             return "SSM"
        return str(arch)

    def classify_architecture_family(self, arch: str) -> str:
        arch_lower = str(arch).lower()
        if arch_lower in ["llama", "qwen", "mistral", "gemma", "phi"]:
            return "Transformer"
        if arch_lower in ["bert", "roberta"]:
            return "Encoder-only Transformer"
        if arch_lower in ["t5", "bart"]:
            return "Encoder-Decoder Transformer"
        if arch_lower in ["mamba", "jamba"]:
            return "State Space Model"
        if "unet" in arch_lower or "dit" in arch_lower:
            return "Diffusion"
        return "Unknown"

    def classify_architecture_generation(self, arch: str, config: Dict[str, Any]) -> str:
        # A simple heuristic to detect generations like "Llama 3" or "Qwen 2.5"
        # Since this usually isn't strongly typed in metadata, we might fall back to Unknown
        model_type = str(config.get("model_type", "")).lower()
        if "llama" in model_type:
            if "3.1" in model_type: return "Llama 3.1"
            if "3" in model_type: return "Llama 3"
            if "2" in model_type: return "Llama 2"
        if "qwen2.5" in model_type: return "Qwen 2.5"
        if "qwen2" in model_type: return "Qwen 2"
        return "Unknown"

    def classify_tokenizer_family(self, tokenizer_config: Dict[str, Any], tokenizer_json: Dict[str, Any]) -> str:
        if "LlamaTokenizer" in str(tokenizer_config.get("tokenizer_class", "")):
            return "BPE (Llama)"
        if "tiktoken" in str(tokenizer_config.get("tokenizer_class", "")).lower():
            return "Tiktoken"
        if "Qwen2Tokenizer" in str(tokenizer_config.get("tokenizer_class", "")):
            return "BPE (Qwen)"
        # Fallback to model type inspecting tokenizer
        if "model" in tokenizer_json:
             model_type = tokenizer_json["model"].get("type", "Unknown")
             return model_type
        return "Unknown"

    def classify_family(self, config: Dict[str, Any], arch: str) -> str:
        """
        Detects the model family.
        """
        model_type = str(config.get("model_type", "")).lower()
        arch_family = self.classify_architecture_family(arch)

        # Audio
        if "whisper" in model_type or "qwen2_audio" in model_type or "audio" in model_type:
             return "Audio"

        # Vision
        if "llava" in model_type or "qwen2_vl" in model_type or "vision" in model_type or "pixtral" in model_type:
            return "Vision-Language"

        # MoE
        if "mixtral" in model_type or "dbrx" in model_type or "moe" in model_type or config.get("num_experts", 0) > 0 or config.get("num_local_experts", 0) > 0:
            return "Mixture of Experts"

        # Diffusion (simple heuristic for now)
        if arch_family == "Diffusion":
            return "Diffusion"

        # Encoder/Embedding
        if "bert" in model_type or "embedding" in model_type or arch_family == "Encoder-only Transformer":
            return "Encoder"

        if "mamba" in model_type or arch_family == "State Space Model":
            return "SSM"

        # Default LLM
        return "Autoregressive"

    def classify_task(self, config: Dict[str, Any], family: str) -> str:
        model_type = str(config.get("model_type", "")).lower()
        if "embedding" in model_type or family == "Encoder":
            return "Embedding"
        if "rerank" in model_type:
            return "Reranking"
        if family == "Audio":
            return "Speech-to-Text"
        if family == "Vision-Language":
             return "Multimodal"
        if family == "Diffusion":
             return "Image-Generation"
        return "Text-Generation"

    def classify_modality(self, family: str, task: str) -> str:
        if family == "Audio":
            return "Audio"
        if family == "Vision-Language":
             return "Text+Image"
        if family == "Diffusion":
             return "Text-to-Image"
        return "Text"

    def classify(self, normalized_config: Dict[str, Any]) -> Tuple[str, str, str, str]:
        """
        Returns (family, architecture, task, modality)
        """
        arch = self.classify_architecture(normalized_config)
        family = self.classify_family(normalized_config, arch)
        task = self.classify_task(normalized_config, family)
        modality = self.classify_modality(family, task)

        return family, arch, task, modality
