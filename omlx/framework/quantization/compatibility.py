# SPDX-License-Identifier: Apache-2.0
"""
Quantization Compatibility Framework.
"""

from typing import Dict, Any, List
from .descriptor import QuantizationDescriptor
from .types import HardwareRecommendation
from omlx.framework.model_intelligence.descriptor import ModelDescriptor

class QuantizationCompatibilityFramework:
    """
    Evaluates compatibility without modifying backend selection.
    """

    def evaluate_model_compatibility(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor) -> bool:
        if not quant_desc.supported_model_families:
             return True # If empty, assume compatible
        return model_desc.model_family in quant_desc.supported_model_families

    def evaluate_backend_compatibility(self, quant_desc: QuantizationDescriptor, backend_desc: Any) -> bool:
        # Assuming backend_desc has a 'name' or 'id'
        backend_id = getattr(backend_desc, 'backend_id', getattr(backend_desc, 'name', 'unknown'))

        # Check against recommended_backend as well as supported
        if quant_desc.recommended_backend and quant_desc.recommended_backend.lower() == str(backend_id).lower():
            return True

        if not quant_desc.supported_backends:
            return True

        return backend_id in quant_desc.supported_backends

    def estimate_hardware_suitability(self, quant_desc: QuantizationDescriptor) -> List[str]:
        suitability = list(quant_desc.recommended_hardware)

        # Add heuristic-based recommendations
        if quant_desc.weight_precision in ("int4", "int3", "int2", "sub_4bit"):
            if HardwareRecommendation.MEMORY_CONSTRAINED.value not in suitability:
                suitability.append(HardwareRecommendation.MEMORY_CONSTRAINED.value)

        if quant_desc.quantization_family.value == "MLX Quantization":
            if HardwareRecommendation.APPLE_SILICON.value not in suitability:
                suitability.append(HardwareRecommendation.APPLE_SILICON.value)
            if HardwareRecommendation.UNIFIED_MEMORY.value not in suitability:
                suitability.append(HardwareRecommendation.UNIFIED_MEMORY.value)

        return suitability

    def generate_compatibility_report(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor, backend_desc: Any) -> Dict[str, Any]:
        return {
             "model_compatible": self.evaluate_model_compatibility(quant_desc, model_desc),
             "backend_compatible": self.evaluate_backend_compatibility(quant_desc, backend_desc),
             "hardware_suitability": self.estimate_hardware_suitability(quant_desc),
             "quantization_family": quant_desc.quantization_family.value
        }
