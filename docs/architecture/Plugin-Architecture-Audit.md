# Plugin Architecture Audit

## 1. Executive Summary

This document provides an audit of the oMLX repository to identify existing and future extension points for the Plugin Framework, in alignment with PLUGIN-001 and RAES-010.

## 2. Existing Extension Points (To be migrated/wrapped)

Currently, extensibility in oMLX is partially handled through hardcoded registries and specific configurations. These need to be transitioned to use the generic Plugin Framework.

### A. Capability Resolver
- **Current State:** Relies on `CapabilityRegistry` to map model architectures to capability traits (e.g., `VisionTrait`, `MoETrait`). Currently uses hardcoded mappings or static discovery.
- **Future State:** Plugins should register `CapabilityPlugin` objects. The `PluginManager` will provide these to the `CapabilityResolver` during the `RuntimeBuilder` bootstrap phase.

### B. Execution Planner passes
- **Current State:** Optimization and transformation passes within the compiler/planner are relatively static.
- **Future State:** `PlannerPlugin` and `OptimizationPlugin` extensions should allow registering new compiler passes (e.g., graph optimizations, cost-model updates).

### C. Lowering & Backend Adapters
- **Current State:** Specific backend adapters (like `MLXBackend` or `MetalBackend`) and lowering passes are hard-linked into the engine.
- **Future State:** Introduce `LoweringPlugin` and `BackendPlugin`. A third-party developer could write a generic Triton backend or a custom cache backend by implementing these contracts and registering them without touching `omlx/engine` code.

### D. Verification
- **Current State:** Testing and verification rely on internal test suites and golden assets.
- **Future State:** `VerificationPlugin` should allow adding custom assertions, test assets, and equivalence checks that the CI pipeline can dynamically pick up.

### E. Tooling & CLI
- **Current State:** The CLI is defined centrally in `omlx/cli.py`.
- **Future State:** `CLIPlugin` extensions should allow dynamic registration of new subcommands (e.g., `omlx quantize --custom-method`).
- **Future State:** `ExporterPlugin` and `VisualizationPlugin` extensions for exporting the graph or viewing IR.

## 3. New Extension Points

To fully support extensibility without modifying the framework, we are introducing the following categories:

- **CapabilityPlugin:** Adds new Model Traits or Features.
- **ValidationPlugin:** Adds new rules to the `ValidationEngine` for descriptor/IR validation.
- **PlannerPlugin:** Modifies or extends the `ExecutionPlanner`'s behavior (e.g., custom cost models).
- **OptimizationPlugin:** Adds transformation passes to the IR.
- **LoweringPlugin:** Converts Logical IR to physical/backend IR.
- **BackendPlugin:** Executes the physical IR.
- **BackendIntelligencePlugin:** Provides hardware telemetry or cost modeling data to the planner.
- **VerificationPlugin:** Integrates new tests into the verification pipeline.
- **ToolingPlugin:** Miscellaneous development tools.
- **CLIPlugin:** Extends the command-line interface.
- **ExporterPlugin:** Adds new formats for exporting execution graphs.
- **VisualizationPlugin:** Adds graph visualization methods.
- **QuantizationPlugin:** Adds custom quantization algorithms.
- **DiagnosticsPlugin:** Captures and reports runtime/compiler diagnostics.

## 4. Hardcoded Registries to Plugin-Aware Transition

The following registries need to be transitioned to consume data provided by the `PluginRegistry`:

1.  **`omlx.registry.capability_registry.CapabilityRegistry`**: Must accept capabilities defined by `CapabilityPlugin` extensions.
2.  **`omlx.registry.model_registry.ModelRegistry`**: Could potentially be extended to load models dynamically from `BackendPlugin`s or custom loaders.
3.  **`omlx.cli.main`**: Needs to query the `PluginContext` or `PluginRegistry` for `CLIPlugin` objects and register their commands via `click` or `argparse`.

## 5. Architectural Invariants (Enforced)

- Plugins do **not** monkey-patch core methods.
- The `PluginRegistry` is sealed and immutable after the `RuntimeBuilder` completes the bootstrap phase.
- Plugins interact exclusively via the explicit `PluginContext` and provided protocols.
- The framework remains 100% functional even if zero plugins are loaded.
