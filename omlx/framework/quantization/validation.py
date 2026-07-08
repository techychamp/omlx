# SPDX-License-Identifier: Apache-2.0
"""
Quantization Validation Framework.
"""

from typing import Dict, Any, List
from .descriptor import QuantizationDescriptor
from .types import QuantizationFamily, ValidationStatus
from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from .planning import QuantizationConversionPlanner

class QuantizationValidator:
    """
    Validates quantization descriptors and metadata for correctness and compatibility.
    """

    def __init__(self):
        self._conversion_planner = QuantizationConversionPlanner()

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

        if desc.quantization_family not in (QuantizationFamily.FP32, QuantizationFamily.FP16, QuantizationFamily.BF16, QuantizationFamily.UNKNOWN):
             if not desc.metadata:
                  warnings.append("Quantized format missing metadata.")

        # New Validations for advanced packing/layout
        if desc.packing_information is not None and not isinstance(desc.packing_information, str):
            is_valid = False
            errors.append("Packing information must be a string if provided.")

        if desc.layout_information is not None and not isinstance(desc.layout_information, str):
            is_valid = False
            errors.append("Layout information must be a string if provided.")

        return {
            "is_valid": is_valid,
            "errors": tuple(errors),
            "warnings": tuple(warnings),
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

             # Also allow recommended_backend
             is_backend_supported = False
             if quant_desc.recommended_backend and quant_desc.recommended_backend.lower() == str(backend_id).lower():
                 is_backend_supported = True
             elif not quant_desc.supported_backends or backend_id in quant_desc.supported_backends:
                 is_backend_supported = True

             if not is_backend_supported:
                 is_valid = False
                 errors.append(f"Backend '{backend_id}' is not supported by this quantization format.")

         return {
             "is_valid": is_valid,
             "errors": tuple(errors),
             "warnings": tuple(warnings),
             "compatibility_status": ValidationStatus.VALID if is_valid else ValidationStatus.INVALID
         }

    def validate_conversion_feasibility(self, source_desc: QuantizationDescriptor, target_family: QuantizationFamily) -> Dict[str, Any]:
        """
        Validates if converting from source descriptor to target family is feasible.
        """
        plan = self._conversion_planner.plan_conversion(source_desc, target_family)
        return {
            "is_feasible": plan.is_feasible,
            "required_tools": plan.required_tools,
            "warnings": plan.warnings
        }
