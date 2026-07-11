# Field Mapping Report: ExecutionProfile to ExecutionPlan

## Fields in ExecutionProfile
- `backend_name`: Mapped from `ExecutionPlan.execution_backend`. (Note: mapping logic needed for `experimental_nemotron`).
- `attention_mode`: Mapped from `ExecutionPlan.execution_hints.get("attention_mode", "causal")`.
- `cache_mode`: Mapped from `ExecutionPlan.cache_strategy`.
- `sampler_mode`: Mapped from `ExecutionPlan.execution_hints.get("sampler_mode", "standard")`.
- `streaming_mode`: Mapped from `ExecutionPlan.execution_mode`.
- `position_encoding`: Mapped from `ExecutionPlan.execution_hints.get("position_encoding", "rope")`.
- `version`: Mapped from `ExecutionPlan.execution_hints.get("version", "v1")`.

## Conclusion
All fields can be mapped. `ExecutionProfileAdapter` will handle the mapping seamlessly.
