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
        if isinstance(arch, list) and arch:
            arch = arch[0]

        arch = str(arch).lower()
        if "llama" in arch:
            return "Transformer"
        elif "qwen" in arch:
            return "Transformer"
        elif "mistral" in arch or "mixtral" in arch:
            return "Transformer"
        elif "bert" in arch or "roberta" in arch:
            return "Transformer"
        elif "unet" in arch:
            return "UNet"
        elif "dit" in arch:
            return "DiT"
        elif "whisper" in arch:
            return "Transformer"
        elif "moe" in arch:
             return "MoE"
        return "Unknown"

    def classify_family(self, config: Dict[str, Any], arch: str) -> str:
        """
        Detects the model family.
        """
        model_type = str(config.get("model_type", "")).lower()

        # Audio
        if "whisper" in model_type or "qwen2_audio" in model_type:
             return "Audio"

        # Vision
        if "llava" in model_type or "qwen2_vl" in model_type or "vision" in model_type:
            return "Vision-Language"

        # MoE
        if "mixtral" in model_type or "dbrx" in model_type or "moe" in model_type or config.get("num_experts", 0) > 0:
            return "Mixture of Experts"

        # Diffusion (simple heuristic for now)
        if "unet" in arch.lower() or "dit" in arch.lower():
            return "Diffusion"

        # Encoder/Embedding
        if "bert" in model_type or "embedding" in model_type:
            return "Encoder"

        # Default LLM
        return "Autoregressive"

    def classify_task(self, config: Dict[str, Any], family: str) -> str:
        model_type = str(config.get("model_type", "")).lower()
        if "embedding" in model_type or family == "Encoder":
            return "Embedding"
        if family == "Audio":
            return "Speech-to-Text"
        if family == "Vision-Language":
             return "Multimodal"
        return "Text-Generation"

    def classify_modality(self, family: str, task: str) -> str:
        if family == "Audio":
            return "Audio"
        if family == "Vision-Language":
             return "Text+Image"
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
