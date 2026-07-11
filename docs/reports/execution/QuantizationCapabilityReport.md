# Quantization Capability Report

Quantization capabilities are strictly exposed as metadata; inference logic is isolated.

## Capability Metadata tracked
- `supported_quantization_families` (e.g. AWQ, GPTQ)
- `supported_quantization_layouts` (e.g. int4, int8)
- `supported_calibration_methods` (e.g. kl_div)
- Boolean flags indicating support for: streaming quantization, diffusion quantization, activation quantization, weight-only quantization, mixed precision, and runtime quantization.
