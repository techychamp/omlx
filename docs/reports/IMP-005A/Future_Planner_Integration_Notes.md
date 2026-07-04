# Future Planner Integration Notes

With `CapabilityResolver` stabilized via IMP-005A, integration into `ExecutionPlanner` (IMP-006) should focus heavily on the consumption of the `CapabilityDescriptor`.

1. **Planner Intake**: The `ExecutionPlanner` should stop reading `config.json` manually and exclusively rely on `CapabilityDescriptor.execution_family` and `CapabilityDescriptor.attention_types`.
2. **Error Logging**: When the Planner rejects an execution graph due to unsupported features (e.g. streaming unavailable), it can query `_diagnostics` internally to emit descriptive errors natively explaining exactly which source disabled streaming.
3. **Execution Hints**: All model optimization overrides should be routed strictly into `descriptor.execution_hints`. The Planner should securely pull them, knowing they cannot be manipulated maliciously down the pipeline.
