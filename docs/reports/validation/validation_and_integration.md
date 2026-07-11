# Validation & Integration Guide

## Validation Guide

The `QuantizationValidator` acts as a crucial safety barrier between model discovery and compiler execution.

### Descriptor Validation
Ensures the internal consistency of the extracted metadata.
- Validates the presence of correct precision mappings.
- Flags corrupted metadata (e.g. negative group sizes).
- Ensures the quantization family is not flagged as `UNKNOWN`.
- Produces a structured report containing boolean validity, `errors`, and `warnings`.

### Compatibility Validation
Cross-references the generated quantization descriptor with the target `ModelDescriptor` and the target Backend.
- Verifies if the chosen backend natively supports the quantization family.
- Verifies if the quantization layout is supported by the target model architecture.

## Compiler Integration Guide

The compiler receives structured quantization information exclusively via the immutable `QuantizationDescriptor`.
- **NO Weight File Inspection**: The compiler must strictly avoid opening or inspecting physical weight shards.
- **Optimization Strategy**: The compiler's execution planner (`ExecutionPlanner`) uses the `QuantizationCostModel` to estimate memory costs, theoretical latency constraints, and optimal streaming topologies without running benchmarks.
- **Dependency Propagation**: Flags like `required_kernels` enable the graph planner to bind explicit lowerings required for execution operations.

## Backend Integration Guide

Backends orchestrate actual kernel execution but are agnostic to file-parsing logic.
- **Consumption**: The `BackendAdapter` consumes the `QuantizationDescriptor` inside the `ExecutionContext`.
- **Branchless Routing**: Adapters use metadata (like `weight_precision` and `group_size`) to resolve appropriate dispatch kernels without querying the model loader.
- **Validation Fallback**: If a backend lacks capability (as diagnosed by the Validator), the Runtime can gracefully fail or fallback without triggering segmentation faults during weight ingestion.
