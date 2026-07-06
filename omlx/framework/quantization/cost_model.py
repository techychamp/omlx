# SPDX-License-Identifier: Apache-2.0
"""
Quantization Cost Model.
"""

from typing import Dict, Any, Tuple
from .descriptor import QuantizationDescriptor
from .types import PerformanceClass
from omlx.framework.model_intelligence.descriptor import ModelDescriptor

class QuantizationCostModel:
    """
    Estimates costs associated with quantization.
    Does NOT benchmark.
    """

    def estimate_memory_usage(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor) -> int:
        bytes_per_param = 2 # default fp16

        wp = quant_desc.weight_precision
        if wp == "int8":
            bytes_per_param = 1
        elif wp in ("int4", "sub_4bit"):
            bytes_per_param = 0.5
        elif wp == "int3":
            bytes_per_param = 0.375
        elif wp == "int2":
            bytes_per_param = 0.25

        return int(model_desc.parameter_count * bytes_per_param)

    def estimate_storage_footprint(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor) -> int:
        return int(self.estimate_memory_usage(quant_desc, model_desc) * 1.05)

    def estimate_throughput(self, quant_desc: QuantizationDescriptor) -> float:
        multiplier = 1.0
        wp = quant_desc.weight_precision
        if wp in ("int4", "sub_4bit"):
            multiplier = 2.0
        elif wp == "int8":
            multiplier = 1.5
        return multiplier

    def estimate_latency(self, quant_desc: QuantizationDescriptor) -> float:
        multiplier = 1.0
        wp = quant_desc.weight_precision
        if wp in ("int4", "sub_4bit"):
            multiplier = 0.5
        elif wp == "int8":
            multiplier = 0.75
        return multiplier

    def estimate_compression_ratio(self, quant_desc: QuantizationDescriptor) -> float:
        wp = quant_desc.weight_precision
        if wp == "int8":
            return 2.0
        elif wp in ("int4", "sub_4bit"):
            return 4.0
        elif wp == "int3":
            return 5.33
        elif wp == "int2":
            return 8.0
        elif wp == "fp32":
            return 0.5
        return 1.0

    def estimate_kernel_complexity(self, quant_desc: QuantizationDescriptor) -> str:
        if quant_desc.mixed_precision or quant_desc.per_channel or quant_desc.quantization_family.value.startswith("IQ"):
            return "HIGH"
        elif quant_desc.weight_precision in ("int4", "int8", "sub_4bit"):
            return "MEDIUM"
        return "LOW"

    def estimate_bandwidth_sensitivity(self, quant_desc: QuantizationDescriptor) -> str:
        if quant_desc.performance_class == PerformanceClass.HIGH:
            return "HIGH"
        elif quant_desc.performance_class == PerformanceClass.MEDIUM:
            return "MEDIUM"
        return "LOW"
