# Roadmap & Technical Debt

## 1. Migration Roadmap (RAES-017)
The oMLX repository is actively executing the **RAES-017 Master Implementation Roadmap**.
The immediate milestones are mapped to specific Boot Phases and Runtime features:
*   **Milestone 1:** Boot & Plugins (`RuntimeBuilder`, `PluginManager`).
*   **Milestone 2:** Adapters & Registry (Deprecating `AdapterFactory`).
*   **Milestone 3:** Execution IR & Planner.
*   **Milestone 4:** Production Ready (Observability, Metrics).

## 2. Requirement: Purging the Legacy Scheduler
A key metric for "Implementation Complete" is the complete removal of the legacy scheduler.
Currently, the legacy scheduler is intertwined with execution specificities. The roadmap requires introducing a temporary `LegacySchedulerShim` to bridge the new Execution Planner to the old Scheduler. Ultimately, the Scheduler must be relegated strictly to queueing, memory constraints, and batching, delegating all actual execution topology directly to the generated Execution IR.

## 3. Technical Debt: Architectural Debt Register
oMLX tracks technical debt strictly via an **Architectural Debt Register** table, rather than relying on scattered `TODO` comments.

**Current Major Technical Debt Items:**
1.  **Global State:** The `_server_state` singleton in `omlx/server.py` bypassing dependency injection. (Remedy: Composition Root).
2.  **Hardcoded Flags:** Boolean capability flags and manual configuration parsing scattered in adapters. (Remedy: Unified `CapabilityDescriptor`).
3.  **Static Factories:** `AdapterFactory` statically mapping models. (Remedy: `AdapterRegistry` and plugin discovery).

## 4. Completion Criteria & Success Metrics
Repository maturity will transition to "Implementation Complete" when:
*   [ ] Legacy scheduler is removed.
*   [ ] Execution Planner is enabled by default.
*   [ ] Adapter Resolver is enabled.
*   [ ] Plugin runtime is enabled.
*   [ ] Golden tests and HF equivalence are passing.
*   [ ] Performance regressions are strictly within budgets (<2% TTFT).
*   [ ] All feature flags are removed.
*   [ ] Architecture fitness tests pass.
