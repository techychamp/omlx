# SPDX-License-Identifier: Apache-2.0
"""
Quantization types and enumerations.
"""

from enum import Enum, auto

class QuantizationFamily(str, Enum):
    """
    Supported quantization families for deterministic classification.
    """
    FP32 = "FP32"
    FP16 = "FP16"
    BF16 = "BF16"
    FP8 = "FP8"
    INT8 = "INT8"
    INT6 = "INT6"
    INT5 = "INT5"
    # Generic precision/storage formats
    INT4 = "INT4"
    INT3 = "INT3"
    INT2 = "INT2"
    NF4 = "NF4"
    AWQ = "AWQ"
    GPTQ = "GPTQ"
    EXL2 = "EXL2"
    # GGUF / specific algorithmic quantization families (e.g., Q4_K_M mapped to Q4)
    Q8 = "Q8"
    Q6 = "Q6"
    Q5 = "Q5"
    Q4 = "Q4"
    Q3 = "Q3"
    Q2 = "Q2"
    QLORA = "QLoRA"
    GGUF = "GGUF Quantization"
    MLX = "MLX Quantization"
    OPTIQ = "OptiQ"
    TURBOQUANT = "TurboQuant"
    OQ = "oQ"
    MIXED_PRECISION = "Mixed Precision"
    DYNAMIC = "Dynamic Quantization"
    STATIC = "Static Quantization"
    UNKNOWN = "Unknown"

class ValidationStatus(str, Enum):
    """
    Structured validation statuses for QuantizationDescriptor.
    """
    VALID = "VALID"
    INVALID = "INVALID"
    WARNING = "WARNING"
    UNKNOWN = "UNKNOWN"
