# Backend Selection Audit

This document audits where backend selection currently occurs, assumptions made about backends, and where the Runtime chooses execution based on BACKEND-003.

## Where backend selection currently occurs
- Previously, backend selection was tightly coupled with instantiation (e.g., hardcoded to select MLXAdapter in `omlx.inference`).

## Where backend assumptions exist
- The inference logic frequently assumed MLX as the implicit execution engine.
- Assumptions regarding memory model and hardware capability were inherently tied to Apple Silicon rather than abstracted through generic metadata.

## Where MLX assumptions exist
- `AdapterRegistry` previously mostly registered MLX explicitly.
- The `CapabilityDescriptor` generation often assumes MLX-specific data types or memory shapes.

## Where runtime chooses execution
- The `RuntimeBuilder` dynamically evaluates environment variables and backend status (often defaulting to a single unified backend without evaluation of alternatives or compatibility).

With the introduction of the Backend Selection Framework, the framework itself is responsible for evaluating, filtering, and scoring candidates before exposing a `selected_backend` inside the execution pipeline, keeping `Runtime` untouched.
