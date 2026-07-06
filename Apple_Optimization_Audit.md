# Apple Optimization Audit

## 1. Device Planning
Device Planning evaluates placement requirements and identifies capabilities (e.g., `omlx/planner/device/planner.py`). It does not alter execution flows or mutate execution objects; instead, it establishes placement hints and hardware availability.

## 2. Compiler
The Compiler pipeline constructs standard Intermediate Representations (LogicalIR, PhysicalIR) and maps models to backend execution architectures using the capability negotiation mechanism. It remains completely insulated from Device Optimization rules via the separation enforced by `PlanningBundle` logic and Optimization Passes.

## 3. Runtime & RuntimeSession
`RuntimeService` and `RuntimeSession` manage session lifecycles without any hardware-specific logic. They only interact with optimizations via the metadata attached to the planning bundle. Ownership of execution is preserved without interference from Apple optimizations.

## 4. ExecutionEngine & Scheduler
The `ExecutionEngine` and `DeterministicGraphExecutor` strictly schedule and execute operations dynamically according to the Dependency Graph, remaining entirely unaffected by hardware-specific optimizations. Scheduling heuristics rely strictly on immutable planning data.

## 5. Graph Framework & Graph Transformation
The Graph Framework models execution dynamically without custom Apple structures. Any optimizations operate entirely on the generalized PlanningBundle and execution metadata rather than bespoke MLX Graph structures.

## 6. Backend
The Apple Backend components implement backend tensor execution through MLX but remain completely unaware of compiler-side Optimization Policies or the broader Placement Analytics passes.

## 7. API
The `omlx.api.v1.compiler` exposes broad compile requests and execution responses cleanly, remaining unpolluted by optimization logic since optimizations manifest solely through diagnostics.

## 8. Tooling
The `OptimizationDiagnostics` and `OptimizationStatistics` provide a rich inspection API for developer tools to interrogate placement heuristics safely.

## User Review Required
The proposed APPLE-002 framework properly isolates the Apple optimization logic using standard Optimization Passes (`OptimizationPass`) over the `PlanningBundle` abstraction, meeting all guidelines.
