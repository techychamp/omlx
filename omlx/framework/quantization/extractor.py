# SPDX-License-Identifier: Apache-2.0
"""
Quantization Capability Extractor.
"""

from typing import Dict, Any, Tuple
from .types import QuantizationFamily

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
            "model_compatibility": tuple()
        }

        # Simple extraction logic
        if family in (QuantizationFamily.INT4, QuantizationFamily.AWQ, QuantizationFamily.GPTQ):
            capabilities["weight_precision"] = "int4"
            capabilities["storage_precision"] = "int4"
            capabilities["compute_precision"] = "fp16"
        elif family == QuantizationFamily.INT8:
            capabilities["weight_precision"] = "int8"
            capabilities["storage_precision"] = "int8"
            capabilities["compute_precision"] = "fp16"

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
