# SPDX-License-Identifier: Apache-2.0
"""
Quantization Cost Model.
"""

from typing import Dict, Any
from .descriptor import QuantizationDescriptor
from omlx.framework.model_intelligence.descriptor import ModelDescriptor

class QuantizationCostModel:
    """
    Estimates costs associated with quantization.
    Does NOT benchmark.
    """

    def estimate_memory_usage(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor) -> int:
        # Simple estimation: parameter count * bytes per param
        bytes_per_param = 2 # default fp16
        if quant_desc.weight_precision == "int4":
            bytes_per_param = 0.5
        elif quant_desc.weight_precision == "int8":
            bytes_per_param = 1

        return int(model_desc.parameter_count * bytes_per_param)

    def estimate_storage_footprint(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor) -> int:
        # Often similar to memory, maybe add some overhead
        return int(self.estimate_memory_usage(quant_desc, model_desc) * 1.05)

    def estimate_throughput(self, quant_desc: QuantizationDescriptor) -> float:
        # Purely arbitrary relative multipliers for theoretical modeling
        multiplier = 1.0
        if quant_desc.weight_precision == "int4":
            multiplier = 2.0
        elif quant_desc.weight_precision == "int8":
            multiplier = 1.5
        return multiplier

    def estimate_latency(self, quant_desc: QuantizationDescriptor) -> float:
        # Purely arbitrary relative multipliers for theoretical modeling
        multiplier = 1.0
        if quant_desc.weight_precision == "int4":
            multiplier = 0.5
        elif quant_desc.weight_precision == "int8":
            multiplier = 0.75
        return multiplier
