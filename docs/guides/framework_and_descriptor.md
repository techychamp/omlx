# OMLX Quantization Framework & Descriptor Guide

## Framework Overview

The OMLX Quantization Framework (QUANT-002) is designed as a universal subsystem that automatically discovers, extracts, classifies, validates, and standardizes model quantization properties into an immutable `QuantizationDescriptor`.

It ensures that execution logic, backend interactions, and compiler stages remain agnostic to the specific quantization format on disk, relying solely on standard metadata representations. The runtime itself does not handle specific quantization logic (e.g., branching for AWQ vs. GGUF).

### Architecture
1. **Classifier**: Determines the specific family (`QuantizationFamily`) of a quantized format.
2. **Extractor**: Extracts parameters from model configuration and mapping them into standard terminology.
3. **Normalizer**: Integrates the Classifier and Extractor into a unified pipeline generating a `QuantizationDescriptor`.
4. **Validator**: Inspects the final descriptor for internal consistency and cross-compatibility with the specific model and backend.

## Quantization Descriptor

The `QuantizationDescriptor` is the immutable source of truth consumed by all downstream compiler and execution processes.

### Key Properties

- `quantization_family`: The determined `QuantizationFamily` enumeration.
- `weight_precision` / `activation_precision`: Defines the target bit widths.
- `storage_precision`: The format used to persist the weights.
- `compute_precision`: The precision required to run inference algorithms.
- `group_size` / `block_size`: Granularity sizes for block-wise quantizations.
- `mixed_precision`: Flag indicating if weights contain diverse precisions.
- `packing_information`: Specific data layout packing metadata.
- `compression_metadata`: Arbitrary metrics specific to individual formats.
- `required_kernels`: A tuple of required kernel interfaces that a backend must implement.
- `validation_status`: Output derived from the Validation subsystem.
