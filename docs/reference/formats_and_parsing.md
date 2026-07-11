# Supported Formats & Metadata Parsing Guide

## Supported Formats Matrix

The framework natively discovers and categorizes the following formats through the `QuantizationFamily` enumeration:

- **Floating Point**: FP32, FP16, BF16, FP8
- **Standard Integer**: INT8, INT6, INT5, INT4, INT3, INT2
- **GGUF Ecosystem**: GGUF Quantization, Q8, Q6, Q5, Q4, Q3, Q2
- **Hugging Face / GPTQ**: GPTQ, AWQ, QLoRA, EXL2
- **Proprietary**: MLX Quantization, OptiQ, TurboQuant, oQ
- **Others**: NF4, Mixed Precision, Dynamic, Static

## Metadata Parsing Guide

The Universal Quantization Framework acts as a metadata abstraction layer. It does not load model weight binary files; rather, it parses structured `config.json`, `quantization_config.json`, or embedded dictionary structures (like those found in `GGUF` metadata blocks).

### 1. Hugging Face (`config.json`)
The parsing layer inspects `quantization_config` to identify the `quant_method`.
- Extracts `group_size`, precision specifics, and maps methods like `exl2`, `awq`, `gptq`, and `bitsandbytes` to internal types.

### 2. GGUF Format
In GGUF files, the framework inspects the header metadata dictionary, primarily reading `general.file_type`.
- Values such as `2` (INT4) or `3` (INT8) are routed to INT4/INT8 classifications.
- Advanced GGUF packing values (`12`-`14` for Q6, `15`-`17` for Q5, `18`-`20` for Q4) are explicitly categorized as Qx formats.

### 3. MLX Format
MLX formats embed a `quantization` sub-dictionary with parameters like `bits`.
- Automatically translated to respective INT structures with block or group metrics.

### 4. Safetensors
For baseline format inspection, unquantized safetensor files often declare native precision (e.g. `format = "pt"`).

### Extraction Logic
The `QuantizationCapabilityExtractor` populates memory profiles based on families:
- **Compute Precision**: Typically upgraded to `fp16`.
- **Storage Precision**: Often compressed to 8-bit or 4-bit containers.
- **Required Kernels**: Dynamically flags dependencies like `awq_gemm` or `exl2_gemm` to ensure downstream execution compatibility.
