# Recommendations for IMP-007

IMP-007 will likely focus on migrating the existing `ExecutionProfileRegistry` over to the `ExecutionPlanner`.

### Suggested Next Steps:
1. **Deprecate `ExecutionProfile`**: Modify the engine initialization to accept an `ExecutionPlan` instead of an `ExecutionProfile`.
2. **Adapter Integration**: Ensure that the Model Adapters know how to read hints from the `ExecutionPlan`.
3. **Advanced Optimization Passes**: Implement concrete passes like `SpeculativeOptimizationPass` or `KVCacheOptimizationPass` using the new registry system.
4. **EventBus Integration**: Fire events like `ExecutionPlanCreated` onto the `EventBus` once a plan is finalized, allowing telemetry systems to observe planning latency.
