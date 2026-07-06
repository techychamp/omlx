# SPDX-License-Identifier: Apache-2.0
"""
Quantization Capability Extractor.
"""

from typing import Dict, Any, Tuple
from .types import QuantizationFamily, ValidationStatus

class QuantizationCapabilityExtractor:
    """
    Extracts capabilities from quantization metadata.
    """

    def extract(self, metadata: Dict[str, Any], family: QuantizationFamily) -> Dict[str, Any]:
        capabilities = {
            "storage_precision": "unknown",
            "compute_precision": "unknown",
            "weight_precision": "unknown",
            "activation_precision": "unknown",
            "kv_cache_precision": "unknown",
            "group_size": None,
            "block_size": None,
            "mixed_precision": False,
            "dynamic_quantization": False,
            "static_quantization": False,
            "per_channel": False,
            "per_group": False,
            "streaming_support": True,
            "batching_support": True,
            "speculative_support": False,
            "backend_compatibility": tuple(),
            "model_compatibility": tuple(),
            "packing_information": None,
            "compression_metadata": {},
            "required_kernels": tuple(),
            "hardware_requirements": tuple(),
            "validation_status": ValidationStatus.UNKNOWN
        }

        # Simple extraction logic
        if family in (QuantizationFamily.INT4, QuantizationFamily.AWQ, QuantizationFamily.GPTQ, QuantizationFamily.EXL2, QuantizationFamily.Q4):
            if family == QuantizationFamily.EXL2:
                capabilities["mixed_precision"] = True
            if family in (QuantizationFamily.AWQ, QuantizationFamily.GPTQ, QuantizationFamily.EXL2):
                capabilities["required_kernels"] = (f"{family.value.lower()}_gemm",)

            capabilities["weight_precision"] = "int4"
            capabilities["storage_precision"] = "int4"
            capabilities["compute_precision"] = "fp16"
        elif family in (QuantizationFamily.INT8, QuantizationFamily.Q8):
            capabilities["weight_precision"] = "int8"
            capabilities["storage_precision"] = "int8"
            capabilities["compute_precision"] = "fp16"
        elif family in (QuantizationFamily.Q6, QuantizationFamily.Q5, QuantizationFamily.Q3, QuantizationFamily.Q2):
            capabilities["weight_precision"] = f"int{family.value[-1]}"
            capabilities["storage_precision"] = "int8" # often stored in 8-bit containers or packed
            capabilities["compute_precision"] = "fp16"
            capabilities["packing_information"] = "packed"
        elif family == QuantizationFamily.OQ:
            capabilities["weight_precision"] = "oq"
            capabilities["storage_precision"] = "oq"
            capabilities["compute_precision"] = "fp16"
        elif family in (QuantizationFamily.FP16, QuantizationFamily.BF16):
            capabilities["weight_precision"] = family.value.lower()
            capabilities["storage_precision"] = family.value.lower()
            capabilities["compute_precision"] = family.value.lower()
        elif family == QuantizationFamily.FP32:
            capabilities["weight_precision"] = "fp32"
            capabilities["storage_precision"] = "fp32"
            capabilities["compute_precision"] = "fp32"

        if "quantization" in metadata and isinstance(metadata["quantization"], dict):
            q = metadata["quantization"]
            if "group_size" in q:
                capabilities["group_size"] = q["group_size"]
                capabilities["per_group"] = True

        if "quantization_config" in metadata and isinstance(metadata["quantization_config"], dict):
            q = metadata["quantization_config"]
            if "group_size" in q:
                capabilities["group_size"] = q["group_size"]
                capabilities["per_group"] = True

        return capabilities
