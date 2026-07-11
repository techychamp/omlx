# Recommendations for IMP-006

1. Ensure the `ExecutionPlanner` operates entirely decoupled from Model raw JSON metadata. The planner must strictly read the `CapabilityDescriptor`.
2. `ExecutionPlanner` should utilize the `_diagnostics` map to generate high-fidelity logs for operators during boot failures, explicitly showing when a feature flag or plugin conflicts with model capabilities.
3. The Cost Model (evaluating memory and latency within the planner) should cleanly rely on `descriptor.execution_hints` knowing they are thread-safe and immutable.
4. Avoid evaluating new constraints inside the Planner that technically belong as `ValidationRule` implementations in the Capability Resolver phase. Keep domain boundaries strict.
