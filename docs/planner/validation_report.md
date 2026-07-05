# Validation Report

Plan validation occurs *after* all optimization passes have run and the `ExecutionPlan` dataclass has been constructed.

Validation is performed by `omlx.planner.validation.validate_plan`.

### Validated Conditions
- **Valid Family**: The `execution_family` must be a recognized enumeration.
- **Backend Presence**: `execution_backend` cannot be empty.
- **Backend Compatibility**: Backends are validated against their parent families (e.g., you cannot use a `diffusion` backend for an `AUTOREGRESSIVE` family).
- **Unique Passes**: Optimization passes must be unique; a pass cannot be applied twice.

### Error Handling
Failures raise a structured `PlannerValidationError` containing a list of strings (`exc.errors`), allowing higher layers to log exact constraints violated.
