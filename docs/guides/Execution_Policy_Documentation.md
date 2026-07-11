# Execution Policy Documentation

## Introduction
The `ExecutionPolicy` is an immutable dataclass representing the context and constraints of how a model should be executed on a backend.

## Properties
- `selected_backend`: The definitive backend chosen by the framework.
- `selection_reason`: A string explanation of why it was chosen (e.g., "highest score based on memory efficiency").
- `selection_policy`: A `BackendSelectionPolicy` enum value (e.g., `BALANCED`, `LATENCY_OPTIMIZED`).
- `fallback_chain`: A tuple of backup backend IDs to try if the primary fails.
- `optimization_preference`: String describing optimization hints.
- `resource_limits`: Dictionary indicating strict limits (e.g., max memory).

## Immutability
To comply with the oMLX architectural constitution, `ExecutionPolicy` is immutable. Once produced, it cannot be mutated by the inference runtime.
