# Recommendations for BACKEND-004

BACKEND-004 should begin integrating this selection framework into the main ExecutionPlanner flow.

1. **Planner Integration:**
   Modify the ExecutionPlanner to generate an `ExecutionPolicy` alongside the `ExecutionPlan`. Currently the planner implicitly assumes the target backend.

2. **Runtime Updates:**
   The `RuntimeBuilder` should invoke `BackendSelectionFramework.select_backend()` during the boot sequence `INITIALIZATION` phase to actually pick the primary backend for the engine to initialize.

3. **Metrics Extraction:**
   Pass the `BackendSelectionDiagnostics` into the Tooling/Metrics framework so the UI can show users exactly why a certain backend was selected and which ones were rejected.
