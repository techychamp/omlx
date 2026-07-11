# ADR-0010: Architectural Consolidation (Optimization, Planning & Runtime)

## Purpose
The repository has matured significantly through the compiler-native architecture, but an architectural audit identified duplicate implementations, disconnected subsystems, and oversized orchestration components causing architectural entropy. The purpose of this milestone (ARCH-CONSOLIDATE-001) is to consolidate, simplify, and strengthen the architecture while strictly preserving all existing behavior and API compatibility.

## Problems
* **Duplicate Pipelines:** The compiler had two optimization pipelines (`omlx/planner/compiler/optimization_pipeline.py` and `omlx/optimization/pipeline.py`).
* **Duplicate Artifacts:** `PlanningBundle` was defined redundantly in both `omlx/planner/bundle.py` and `omlx/planner/domains/bundle.py`.
* **Disconnected Subsystems:** `optimization/intelligence/` (Optimization Planner, Policy, Telemetry) and `optimization/apple/` (Apple Silicon optimizations) were floating subsystems not fully integrated into the canonical pipeline.
* **Oversized Components:** The `GraphScheduler` in `omlx/runtime/scheduling/scheduler.py` handles parsing, heuristics, and execution queue emission within monolithic blocks.

## Alternatives Considered
* **Retain both pipelines:** One for logical IR, one for pass scheduling. Rejected because they overlapped responsibilities entirely.
* **Complete Scheduler Rewrite:** Rejected because this milestone focuses strictly on consolidation and preparation (no new functionality), and a full rewrite risks introducing regressions.

## Chosen Architecture
* **Canonical Optimization Pipeline:** `omlx/optimization/pipeline.py` with `PassManager` is the single source of truth for both `LOGICAL_IR` and `PHYSICAL_IR` passes. The `OptimizationPlanner` (Intelligence) wraps this to select passes dynamically.
* **Canonical Planning Bundle:** `omlx/planner/domains/bundle.py` is the sole `PlanningBundle`.
* **Integrated Subsystems:** Apple optimizations run specifically on the `EXECUTION_PLAN` stage via the unified pipeline before logic-lowering.

## Public Contract Verification
This consolidation is completely invisible externally.
* **API:** No changes.
* **Runtime Behavior:** No changes.
* **Serialization:** Preserved natively.
* **Configuration:** Unchanged.
* **Plugin Contract:** No plugin interfaces altered.
* **Compiler Output:** Identical execution graphs generated.

## Consolidation Metrics
* **Before:**
  * `PlanningBundle` implementations: 2
  * Optimization pipelines: 2
  * Disconnected optimization packages: 2 (`apple`, `intelligence`)
* **After:**
  * `PlanningBundle` implementations: 1
  * Optimization pipelines: 1
  * Disconnected optimization packages: 0 (All Integrated)

## Future Work
* Extract `GraphScheduler` logic based on the Scheduler Decomposition Report (SCHED-003).
