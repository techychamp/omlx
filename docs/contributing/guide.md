# Contributor Guide

## 1. Submitting Code
oMLX uses trunk-based development. Large feature branches are strictly forbidden.
*   **PR Size:** Keep Pull Requests small (maximum ~5 files changed).
*   **Checkpoints:** Structure work into 1-3 day checkpoints.

## 2. Architectural Decisions (ADRs)
Significant architectural changes require an **Architectural Decision Record (ADR)** filed under `docs/architecture/adrs/`.
*   **Template Requirements:** Title, Status, Context, Decision, Consequences, Alternatives Considered, Migration Analysis, Verification Impact, Rollback Analysis.
*   **Approval:** Must be approved by an Architecture Maintainer.

## 3. Architectural Exceptions
If a temporary workaround is needed that violates a core invariant (see RAES-015), it requires an **Architectural Exception ADR**. It must include:
*   Justification.
*   Hard expiration date / version.
*   Migration plan back to constitutionality.
*   Designated Review Owner.

## 4. How to Add an Execution Backend
1.  Define a new `ExecutionBackendExtension` declaring the backend capabilities via a `BackendDescriptor`.
2.  Implement the backend translation logic to map Physical IR to backend-specific hardware operations.
3.  Register the extension via the `PluginContext`.
4.  Ensure it passes the Backend Verification Suite (HF equivalence, TTFT budgets).

## 5. How to Add a Compiler Pass
1.  Implement a new `PlanningPass` (Analysis, Rewrite, or Validation).
2.  Ensure the pass complies with the strict immutability invariant: **Do not mutate existing IR**. Rewrite passes must output a new, transformed IR graph.
3.  Inject the pass into the `PassRegistry`.

## 6. How to Add a Capability
1.  Define the capability schema (must be deeply immutable).
2.  Update the `CapabilityResolver` (or create a new `PluginSource`) to detect and emit this capability.
3.  Update the `ExecutionPlanner` cost models or strategy selectors to utilize the new capability.

## 7. How to Add Validation Rules
1.  Implement a stateless `ValidationRule`.
2.  Ensure it does not mutate descriptors or cache mutable data to remain thread-safe.
3.  Register it with the `ValidationRegistry`.
