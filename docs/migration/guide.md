# Migration Guide

## 1. Overview
The oMLX repository is actively migrating from a legacy, hardcoded execution model to a capability-driven Compiler Architecture as defined in RAES-006 through RAES-016. This migration is guided by the **RAES-017 Master Implementation Roadmap**, designed as a low-risk, checkpoint-driven program without introducing new architectural abstractions.

## 2. Legacy Architecture vs. Compiler Architecture
*   **Legacy:** Hardcoded boolean flags in capabilities, manual capability resolution, intertwined scheduler and execution logic, static adapter factories, and a lack of a unified composition root (relying on `_server_state`).
*   **New Architecture:** Modular `CapabilityDescriptor`s, unified `RuntimeBuilder` Composition Root, Execution Planner owning the execution graph, and declarative Plugins.

## 3. Migration Phases (RAES-017)
The migration is executed in strict phases:
1.  **Phase 1: Composition Root & Bootstrap.** Implement `RuntimeBuilder`.
2.  **Phase 2: Plugin Runtime.** Implement `PluginManager` and Event System.
3.  **Phase 3: Unified Model Adapters.** Deprecate `AdapterFactory`.
4.  **Phase 4: Execution Planner Integration.** Connect the planner to the core, decoupling the Scheduler.
5.  **Phase 5: Execution IR Generation & Lowering.** Fully abstract execution into Logical/Physical IR.
6.  **Phase 6: Production Operations.** Observability, Telemetry, and CI/CD pipelines.

## 4. Feature Flags & Shadow Modes
All experimental and migration features are strictly gated by feature flags prefixed with `OMLX_FF_` (or historically `OMLX_EXPERIMENTAL_`).
*   Flags safely isolate in-flight capabilities.
*   They are owned by the specific developer/ADR introducing the feature.
*   They evaluate *only* at the Composition Root.
*   They must be removed when the feature transitions to Beta or Stable.

## 5. Compatibility Layers & Rollback
Temporary compatibility layers (e.g., `LegacySchedulerShim`) bridge the old components to the new ones to ensure the repository remains buildable and testable at all times.
If an issue arises, the system can quickly rollback by toggling the feature flag to revert to the old hardcoded discovery paths or implementations.
Once a phase completes and passes verification (Golden tests, Performance bounds), the compatibility layer is purged (e.g., purging `_server_state` or `AdapterFactory`).
