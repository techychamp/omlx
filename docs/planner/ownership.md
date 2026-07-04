# Planner Ownership Report

The ownership model is strictly hierarchical and deterministic:

1. **`RuntimeBuilder`** is responsible for creating dependencies (e.g., `PassRegistry`) if needed.
2. **`Runtime`** strictly *owns* exactly one instance of the `ExecutionPlanner`.
3. **`ExecutionPlanner`** strictly *owns* a `PassRegistry`.
4. **`ExecutionPlan`** is *owned* by whichever caller invokes `planner.plan()`, but because it is immutable, ownership is trivial (it can be shared safely across threads).

There are no module-level global planners.
