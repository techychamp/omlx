# SPDX-License-Identifier: Apache-2.0
"""
Quantization Compatibility Framework.
"""

from typing import Dict, Any, List
from .descriptor import QuantizationDescriptor
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
        if not quant_desc.supported_backends:
            return True
        return backend_id in quant_desc.supported_backends

    def generate_compatibility_report(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor, backend_desc: Any) -> Dict[str, Any]:
        return {
             "model_compatible": self.evaluate_model_compatibility(quant_desc, model_desc),
             "backend_compatible": self.evaluate_backend_compatibility(quant_desc, backend_desc),
             "quantization_family": quant_desc.quantization_family.value
        }
