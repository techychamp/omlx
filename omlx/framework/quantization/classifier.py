# SPDX-License-Identifier: Apache-2.0
"""
Quantization Classifier.
"""

from typing import Dict, Any
from .types import QuantizationFamily

class QuantizationClassifier:
    """
    Deterministically classifies quantization families from metadata.
    """

    def classify_mlx(self, metadata: Dict[str, Any]) -> QuantizationFamily:
        if "quantization" in metadata:
            q_info = metadata["quantization"]
            if isinstance(q_info, dict):
                bits = q_info.get("bits", 0)
                if bits == 4:
                    return QuantizationFamily.INT4
                if bits == 8:
                    return QuantizationFamily.INT8
            return QuantizationFamily.MLX
        return QuantizationFamily.UNKNOWN

    def classify_gguf(self, metadata: Dict[str, Any]) -> QuantizationFamily:
        # Simplistic gguf classifier based on arbitrary heuristics
        file_type = metadata.get("general.file_type", -1)
        if file_type == 2:
            return QuantizationFamily.INT4
        if file_type == 3:
            return QuantizationFamily.INT8
        if file_type == 7:
            return QuantizationFamily.Q8
        if file_type in (12, 13, 14):
            return QuantizationFamily.Q6
        if file_type in (15, 16, 17):
            return QuantizationFamily.Q5
        if file_type in (18, 19, 20):
            return QuantizationFamily.Q4
        if file_type in (21, 22, 23):
            return QuantizationFamily.Q3
        if file_type in (24, 25, 26):
            return QuantizationFamily.Q2
        if "gguf" in str(metadata).lower():
            return QuantizationFamily.GGUF
        return QuantizationFamily.UNKNOWN

    def classify_safetensors(self, metadata: Dict[str, Any]) -> QuantizationFamily:
        if "format" in metadata and metadata["format"] == "pt":
            # TODO: Safetensors classification should eventually rely on metadata,
            # config, or tensor inspection rather than defaulting to FP16.
            # Attempt to infer precision based on common patterns or defaults
            # (In a real implementation, this would inspect tensor dtypes)
            return QuantizationFamily.FP16 # Assumption for testing
        return QuantizationFamily.UNKNOWN

    def classify_hf(self, config: Dict[str, Any]) -> QuantizationFamily:
        if "quantization_config" in config:
            q_config = config["quantization_config"]
            method = q_config.get("quant_method", "").lower()
            if method == "awq":
                return QuantizationFamily.AWQ
            elif method == "gptq":
                return QuantizationFamily.GPTQ
            elif method == "bitsandbytes":
                return QuantizationFamily.INT8 # Simplification
            elif method == "exl2":
                return QuantizationFamily.EXL2
            elif method == "oq":
                return QuantizationFamily.OQ
        return QuantizationFamily.UNKNOWN
