def write_report(filename, content):
    with open(filename, "w") as f:
        f.write(content)

write_report("Ownership_Report.md", """# Ownership Report

- **Runtime**: Owns request lifecycle, session lifecycle, and execution coordination. Does NOT own batching policy.
- **Planning**: Owns request compatibility, batch composition, and resource requirements through the deterministic `BatchPlanner`.
- **Compiler**: Owns `BatchPlan` generation and composition, producing immutable batch descriptions without executing.
- **GenerationStrategy**: Owns execution intent and policy via `BatchGenerationStrategy`.
- **Scheduler**: Owns dependency and execution ordering.
- **ExecutionEngine**: Consumes `PlanningBundle` (including `BatchPlan`) to execute.
- **Backend**: Executes operations, unaware of batching.
- **Observability**: Passively records metrics.
- **API**: Exposes configurations.
- **Tooling**: Inspects artifacts.
""")

write_report("Planning_Composition_Report.md", """# Planning Composition Report

The `PlanningBundle` has been updated to include `batch_plan: Optional[BatchPlan] = None`. This ensures that batching planning artifacts are composed immutably alongside execution, device, cache, memory, and verification plans.
""")

write_report("Scheduler_Compatibility_Report.md", """# Scheduler Compatibility Report

The Scheduler continues to own execution and dependency ordering. It will consume the `BatchPlan` embedded within the `PlanningBundle` without altering its internal scheduling policies. The batching logic is kept entirely outside the Scheduler, adhering strictly to the architectural constraints.
""")

write_report("Future_Continuous_Batching_Report.md", """# Future Continuous Batching Report

The current `BatchPlanner` and `BatchPlan` structure provides a deterministic, immutable foundation. Continuous batching (BATCH-002) can be implemented by creating continuous batch planning domains that output updated `BatchPlan` artifacts per scheduler tick, without requiring architectural redesigns of the Runtime or Backend.
""")

write_report("Batch_Planning_Guide.md", """# Batch Planning Guide

1. Use `BatchPlanner.plan(request_ids, max_batch_size, max_tokens)` to create a `BatchPlan`.
2. The plan produces a `BatchDescriptor`, `BatchRequirement`, and `BatchCompatibilityReport`.
3. Include the `BatchPlan` in the `PlanningBundle`.
""")

write_report("Batch_Strategy_Guide.md", """# Batch Strategy Guide

Use `BatchGenerationStrategy` when handling batched requests. It sets the execution intent to `"batch"` and cache policy to `"batch_optimized"`.
""")

write_report("Runtime_Batch_Guide.md", """# Runtime Batch Guide

The Runtime receives the `PlanningBundle` containing the `BatchPlan` and orchestrates execution via the ExecutionEngine. It must never construct batches itself.
""")

write_report("Scheduler_Integration_Guide.md", """# Scheduler Integration Guide

The Scheduler reads `BatchPlan` from the `PlanningBundle` to understand the grouping of requests but must not alter or decide batching policies.
""")

write_report("Planning_Domain_Guide.md", """# Planning Domain Guide

Planning Domains communicate exclusively through immutable artifacts composed in the `PlanningBundle`. `BatchPlanner` is an independent domain.
""")

write_report("Architecture_Decision_Record_BATCH_001.md", """# ADR: Compiler-Native Batch Execution

**Decision**: Introduce compiler-native batch execution as an independent Planning Domain and Generation Strategy, preserving existing Runtime, Scheduler, and Backend architectures.
**Rationale**: Keeps batching policy isolated, deterministic, and immutable.
""")

write_report("Migration_Report_BATCH_001.md", """# Migration Report BATCH-001

Successfully introduced `BatchPlanner`, `BatchPlan` artifacts, and `BatchGenerationStrategy`. Updated `PlanningBundle` to compose `BatchPlan`. No architectural changes required in core execution components.
""")

write_report("Future_Continuous_Batching_Guide.md", """# Future Continuous Batching Guide

Building on BATCH-001, future continuous batching will iterate on `BatchPlan` generation during execution pauses, preserving the immutable artifact flow to the ExecutionEngine.
""")
