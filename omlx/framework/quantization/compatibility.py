# SPDX-License-Identifier: Apache-2.0
"""
Quantization Compatibility Framework.
"""

from typing import Dict, Any, List, Tuple
from .descriptor import QuantizationDescriptor
from .types import HardwareRecommendation
from omlx.framework.model_intelligence.descriptor import ModelDescriptor

class QuantizationCompatibilityFramework:
    """
    Evaluates compatibility without modifying backend selection.
    """

    _model_compat_cache: Dict[Tuple[int, int], bool] = {}
    _backend_compat_cache: Dict[Tuple[int, str], bool] = {}

    def evaluate_model_compatibility(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor) -> bool:
        cache_key = (id(quant_desc), id(model_desc))
        if cache_key in self._model_compat_cache:
            return self._model_compat_cache[cache_key]

        if not quant_desc.supported_model_families:
             result = True # If empty, assume compatible
        else:
             result = model_desc.model_family in quant_desc.supported_model_families

        self._model_compat_cache[cache_key] = result
        return result

    def evaluate_backend_compatibility(self, quant_desc: QuantizationDescriptor, backend_desc: Any) -> bool:
        backend_id = getattr(backend_desc, 'backend_id', getattr(backend_desc, 'name', 'unknown'))
        cache_key = (id(quant_desc), backend_id)
        if cache_key in self._backend_compat_cache:
            return self._backend_compat_cache[cache_key]

        if not quant_desc.supported_backends:
            result = True
        else:
            result = backend_id in quant_desc.supported_backends

        self._backend_compat_cache[cache_key] = result
        return result

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
