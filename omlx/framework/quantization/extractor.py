# SPDX-License-Identifier: Apache-2.0
"""
Quantization Capability Extractor.
"""

from typing import Dict, Any, Tuple
from .types import QuantizationFamily, ValidationStatus, PerformanceClass, HardwareRecommendation

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
            "layout_information": None,
            "alignment_information": None,
            "compression_metadata": {},
            "compression_ratio": None,
            "estimated_memory_usage": None,
            "estimated_bandwidth_usage": None,
            "required_kernels": tuple(),
            "hardware_requirements": tuple(),
            "recommended_backend": None,
            "recommended_hardware": tuple(),
            "conversion_compatibility": tuple(),
            "performance_class": PerformanceClass.UNKNOWN,
            "validation_status": ValidationStatus.UNKNOWN
        }

        # Simple extraction logic with enhanced intelligence
        if family in (QuantizationFamily.INT4, QuantizationFamily.AWQ, QuantizationFamily.GPTQ, QuantizationFamily.EXL2, QuantizationFamily.Q4, QuantizationFamily.IQ4_XS, QuantizationFamily.IQ4_NL):
            if family == QuantizationFamily.EXL2:
                capabilities["mixed_precision"] = True
                capabilities["required_kernels"] = ("exl2_gemm", "dequantize_exl2")
                capabilities["recommended_backend"] = "CUDA"
                capabilities["recommended_hardware"] = (HardwareRecommendation.DISCRETE_GPU.value,)
            elif family == QuantizationFamily.AWQ:
                capabilities["required_kernels"] = ("awq_gemm",)
                capabilities["recommended_backend"] = "CUDA"
                capabilities["recommended_hardware"] = (HardwareRecommendation.DISCRETE_GPU.value,)
                capabilities["packing_information"] = "awq_packed"
                capabilities["layout_information"] = "awq_layout"
            elif family == QuantizationFamily.GPTQ:
                capabilities["required_kernels"] = ("gptq_gemm",)
                capabilities["packing_information"] = "gptq_packed"
            elif family in (QuantizationFamily.IQ4_XS, QuantizationFamily.IQ4_NL):
                capabilities["required_kernels"] = ("iq_gemm", "dequantize_iq")
                capabilities["packing_information"] = "iq_packed"
                capabilities["recommended_backend"] = "CPU"
                capabilities["recommended_hardware"] = (HardwareRecommendation.CPU_ONLY.value,)

            capabilities["weight_precision"] = "int4"
            capabilities["storage_precision"] = "int4"
            capabilities["compute_precision"] = "fp16"
            capabilities["performance_class"] = PerformanceClass.HIGH

        elif family in (QuantizationFamily.INT8, QuantizationFamily.Q8):
            capabilities["weight_precision"] = "int8"
            capabilities["storage_precision"] = "int8"
            capabilities["compute_precision"] = "fp16"
            capabilities["performance_class"] = PerformanceClass.MEDIUM
            capabilities["required_kernels"] = ("int8_gemm",)

        elif family in (QuantizationFamily.Q6, QuantizationFamily.Q5, QuantizationFamily.Q3, QuantizationFamily.Q2, QuantizationFamily.IQ3_XXS, QuantizationFamily.IQ3_S, QuantizationFamily.IQ2_XXS, QuantizationFamily.IQ2_XS, QuantizationFamily.IQ2_S, QuantizationFamily.IQ1_S, QuantizationFamily.IQ1_M):
            capabilities["weight_precision"] = f"int{family.value[-1]}" if ("Q" in family.value and "IQ" not in family.value and "Q8" not in family.value) else "sub_4bit"
            capabilities["storage_precision"] = "int8" # often stored in 8-bit containers or packed
            capabilities["compute_precision"] = "fp16"
            capabilities["packing_information"] = "packed"
            capabilities["required_kernels"] = ("gguf_gemm", f"dequantize_{family.value.lower()}")
            capabilities["performance_class"] = PerformanceClass.HIGH

        elif family == QuantizationFamily.OQ:
            capabilities["weight_precision"] = "oq"
            capabilities["storage_precision"] = "oq"
            capabilities["compute_precision"] = "fp16"
            capabilities["required_kernels"] = ("oq_gemm",)

        elif family in (QuantizationFamily.FP16, QuantizationFamily.BF16):
            capabilities["weight_precision"] = family.value.lower()
            capabilities["storage_precision"] = family.value.lower()
            capabilities["compute_precision"] = family.value.lower()
            capabilities["required_kernels"] = (f"{family.value.lower()}_gemm",)
            capabilities["performance_class"] = PerformanceClass.LOW
            capabilities["recommended_hardware"] = (HardwareRecommendation.LARGE_MEMORY.value,)

        elif family == QuantizationFamily.FP32:
            capabilities["weight_precision"] = "fp32"
            capabilities["storage_precision"] = "fp32"
            capabilities["compute_precision"] = "fp32"
            capabilities["required_kernels"] = ("fp32_gemm",)
            capabilities["performance_class"] = PerformanceClass.LOW

        elif family == QuantizationFamily.MLX:
            capabilities["recommended_backend"] = "MLX"
            capabilities["recommended_hardware"] = (HardwareRecommendation.APPLE_SILICON.value, HardwareRecommendation.UNIFIED_MEMORY.value)
            capabilities["required_kernels"] = ("mlx_gemm",)

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
