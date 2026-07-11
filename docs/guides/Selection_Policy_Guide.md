# Selection Policy Guide

## The Need for Policies
Different environments have different requirements. A local developer machine prioritizes latency, while a production cluster prioritizes throughput. Policies allow users to state their goals without writing custom scoring logic.

## Supported Policies
- **LATENCY_OPTIMIZED**: Weights lower execution latency highest.
- **MEMORY_OPTIMIZED**: Strongly penalizes memory usage, ideal for low VRAM systems.
- **BALANCED**: Default scoring mechanism balancing all constraints.
- **ENERGY_EFFICIENT**: (Future) Prefers backends with lower power consumption profiles.
- **MAXIMUM_THROUGHPUT**: Prefers continuous batching and high utilization limits.
- **DEVELOPER_OVERRIDE**: Strict adherence to a manually selected backend (even if suboptimal).

## How it works
The `BackendSelectionFramework` checks `policy.selection_policy` during evaluation and applies multipliers to the raw score produced by the `BackendEvaluationReport`.
