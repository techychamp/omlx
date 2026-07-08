# SPDX-License-Identifier: Apache-2.0
"""
Quantization Conversion Planning Framework.
"""

from dataclasses import dataclass
from typing import Tuple, Optional
from .types import QuantizationFamily
from .descriptor import QuantizationDescriptor

@dataclass(frozen=True)
class ConversionPlan:
    """
    Immutable representation of a quantization conversion plan.
    Represents feasibility only, does not perform conversion.
    """
    source_family: QuantizationFamily
    target_family: QuantizationFamily
    is_feasible: bool
    estimated_memory_cost: Optional[int]
    estimated_time_cost: Optional[str] # e.g. "LOW", "HIGH"
    required_tools: Tuple[str, ...]
    warnings: Tuple[str, ...]

class QuantizationConversionPlanner:
    """
    Generates immutable conversion plans evaluating feasibility.
    """

    def plan_conversion(self, source_desc: QuantizationDescriptor, target_family: QuantizationFamily) -> ConversionPlan:
        """
        Determines the feasibility of converting from the given source format to a target format.
        """
        source_family = source_desc.quantization_family
        is_feasible = False
        required_tools = []
        warnings = []

        # Simple heuristic rule-based conversion planning without execution
        if source_family == QuantizationFamily.FP16 or source_family == QuantizationFamily.BF16:
            # High precision can be converted to most lower precision formats
            if target_family in (QuantizationFamily.INT4, QuantizationFamily.INT8, QuantizationFamily.AWQ, QuantizationFamily.GPTQ, QuantizationFamily.GGUF, QuantizationFamily.MLX, QuantizationFamily.OQ):
                is_feasible = True
                if target_family == QuantizationFamily.MLX:
                    required_tools.append("mlx_lm.convert")
                elif target_family == QuantizationFamily.GGUF:
                    required_tools.append("llama.cpp convert.py")

        elif source_family == QuantizationFamily.Q4:
            if target_family in (QuantizationFamily.Q6, QuantizationFamily.Q8):
                # Upcasting is generally feasible but not recommended
                is_feasible = True
                warnings.append("Upcasting quantization does not improve model quality.")
            elif target_family == QuantizationFamily.OQ:
                is_feasible = True
                required_tools.append("oq_convert")

        elif source_family == QuantizationFamily.AWQ:
            if target_family == QuantizationFamily.GGUF:
                is_feasible = True
                required_tools.append("llama.cpp convert.py")

        elif source_family == QuantizationFamily.GPTQ:
            if target_family == QuantizationFamily.MLX:
                is_feasible = True
                required_tools.append("mlx_lm.convert")

        return ConversionPlan(
            source_family=source_family,
            target_family=target_family,
            is_feasible=is_feasible,
            estimated_memory_cost=None,
            estimated_time_cost="UNKNOWN",
            required_tools=tuple(required_tools),
            warnings=tuple(warnings)
        )
