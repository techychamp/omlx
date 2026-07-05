# SPDX-License-Identifier: Apache-2.0
"""
Quantization Diagnostics.
"""

from typing import Dict, Any, List
from .descriptor import QuantizationDescriptor
from .compatibility import QuantizationCompatibilityFramework
from .cost_model import QuantizationCostModel
from omlx.framework.model_intelligence.descriptor import ModelDescriptor

class QuantizationDiagnostics:
    """
    Generates diagnostic reports for quantization.
    """

    def __init__(self):
        self._compatibility = QuantizationCompatibilityFramework()
        self._cost_model = QuantizationCostModel()

    def generate_summary(self, desc: QuantizationDescriptor) -> Dict[str, Any]:
        return {
            "family": desc.quantization_family.value,
            "weight_precision": desc.weight_precision,
            "group_size": desc.group_size
        }

    def generate_cost_report(self, desc: QuantizationDescriptor, model_desc: ModelDescriptor) -> Dict[str, Any]:
         return {
             "estimated_memory_bytes": self._cost_model.estimate_memory_usage(desc, model_desc),
             "estimated_storage_bytes": self._cost_model.estimate_storage_footprint(desc, model_desc),
             "throughput_multiplier": self._cost_model.estimate_throughput(desc),
             "latency_multiplier": self._cost_model.estimate_latency(desc)
         }
