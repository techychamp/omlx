# oMLX Architecture Scorecard: Checkpoint a46ab94

This scorecard ranks the architectural health, changes, and risks introduced by checkpoint `a46ab94` ("added foundation for triage & updated scheduler").

---

## 1. Metrics Scorecard

| Architectural Metric | Score / Delta | Evaluation & Rationale |
| :--- | :--- | :--- |
| **Architecture Score** | **88 / 100** | Good structural core, but penalized for introducing `AttributeError` regressions on legacy mocks and failing memory threshold checks. |
| **Complexity Delta** | **+58 lines** | Moderate increase in code size due to setup in `EngineCore`. Simplifies core scheduler logic but duplicates paths. |
| **Coupling Delta** | **Reduced (Core)** | Successfully decouples scheduler from model execution, but introduces minor mock coupling due to non-defensive attribute access. |
| **Technical Debt** | **Medium (Added)**| Broad catch-all exception swallowing in `EngineCore` and non-defensive `self.strategy` queries in `Scheduler`. |
| **Future Risk** | **Low-Medium** | High code safety via fallbacks, but memory object counts in integration environments need isolation checks. |
| **Rollback Quality** | **Excellent (9/10)** | Modular strategy binding. Reverting requires removing only core instantiation and delegation checks. |
| **Test Coverage** | **Failing (6075/6077)**| 2 failures observed: prefill OOM graceful test due to `AttributeError` and decode delegation test due to leak threshold. |
| **Maintainability Score** | **89 / 100** | Good separation of concern. Moving stubs to strategies reduces scheduler bloat, but must clean up fallbacks. |

---

## 2. Invariant Verification Checklist

| Architectural Invariant Check | Status | Verification Evidence / Rationale |
| :--- | :--- | :--- |
| **No Scheduler Coupling** | **Passed** | AST static test `test_scheduler_static_invariants` verifies the scheduler has zero references to registry layers. |
| **No Backend Coupling** | **Passed** | Scheduler does not import or refer to execution backends; it communicates solely with the abstract strategy. |
| **No Execution Leaks** | **Failed** | `test_memory_stability_and_leaks` failed: object delta count was 1,039 over 50 iterations, exceeding the < 100 threshold. |
| **No Model-Name Coupling** | **Passed** | No new model name strings are referenced. Legacies exist but were not introduced in this checkpoint. |
| **No UI Coupling** | **Passed** | Purely backend execution layers are modified; zero impact or coupling to Swift UI app or server API endpoints. |

---

## 3. Metric Definitions

- **Architecture Score (0-100)**: Evaluates overall compliance with the Project Constitution (separation of concerns, layering, and invariants).
- **Complexity Delta**: The net change in cognitive load or system paths introduced by the changes.
- **Coupling Delta**: The shift in dependency strength between modules (e.g. Scheduler to ExecutionBackend).
- **Technical Debt**: Assessment of the code quality trade-offs or stubs introduced for speed of delivery.
- **Future Risk**: Likelihood of the changes causing regressions in existing/future workflows (e.g., Metal memory constraints, multi-threaded races).
- **Rollback Quality (1-10)**: Ease of reverting the changes without impacting adjacent features.
- **Test Coverage**: Presence of unit and integration tests specifically covering the modified and introduced logic.
- **Maintainability Score (0-100)**: Long-term developer ergonomics (readability, extension simplicity).
