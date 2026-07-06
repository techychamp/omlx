# SPDX-License-Identifier: Apache-2.0
"""
Quantization Validation Framework.
"""

from typing import Dict, Any, List
from .descriptor import QuantizationDescriptor
from .types import QuantizationFamily, ValidationStatus
from omlx.framework.model_intelligence.descriptor import ModelDescriptor

class QuantizationValidator:
    """
    Validates quantization descriptors and metadata for correctness and compatibility.
    """

    def validate_descriptor(self, desc: QuantizationDescriptor) -> Dict[str, Any]:
        """
        Validates the structure and consistency of a QuantizationDescriptor.
        """
        is_valid = True
        errors = []
        warnings = []

        if desc.quantization_family == QuantizationFamily.UNKNOWN:
            is_valid = False
            errors.append("Quantization family is UNKNOWN.")

        if desc.group_size is not None and desc.group_size <= 0:
            is_valid = False
            errors.append(f"Invalid group size: {desc.group_size}. Must be positive.")

        if desc.block_size is not None and desc.block_size <= 0:
            is_valid = False
            errors.append(f"Invalid block size: {desc.block_size}. Must be positive.")

        if desc.weight_precision == "unknown":
            is_valid = False
            errors.append("Weight precision is unknown.")

        if desc.storage_precision == "unknown":
            is_valid = False
            errors.append("Storage precision is unknown.")

        # Check for missing metadata for quantized formats
        if desc.quantization_family not in (QuantizationFamily.FP32, QuantizationFamily.FP16, QuantizationFamily.BF16, QuantizationFamily.UNKNOWN):
             if not desc.metadata:
                  warnings.append("Quantized format missing metadata.")

        return {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "validation_status": ValidationStatus.VALID if is_valid else ValidationStatus.INVALID
        }

    def validate_compatibility(self, quant_desc: QuantizationDescriptor, model_desc: ModelDescriptor, backend_desc: Any = None) -> Dict[str, Any]:
         """
         Validates compatibility between quantization, model, and optionally backend.
         """
         is_valid = True
         errors = []
         warnings = []

         # Model compatibility
         if quant_desc.supported_model_families and model_desc.model_family not in quant_desc.supported_model_families:
             is_valid = False
             errors.append(f"Model family '{model_desc.model_family}' is not supported by this quantization format.")

         # Backend compatibility (if provided)
         if backend_desc is not None:
             backend_id = getattr(backend_desc, 'backend_id', getattr(backend_desc, 'name', 'unknown'))
             if quant_desc.supported_backends and backend_id not in quant_desc.supported_backends:
                 is_valid = False
                 errors.append(f"Backend '{backend_id}' is not supported by this quantization format.")

         return {
             "is_valid": is_valid,
             "errors": errors,
             "warnings": warnings,
             "compatibility_status": ValidationStatus.VALID if is_valid else ValidationStatus.INVALID
         }
