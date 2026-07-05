# API Reference

## 1. API Stability Levels
oMLX strictly classifies APIs using Architectural Maturity Levels to dictate stability and deprecation guarantees (RAES-015):

*   **Level 0 — Experimental:** Triage, streaming MoE, experimental diffusion. No API stability guaranteed. Subject to removal without notice.
*   **Level 1 — Prototype:** Early stage APIs. Minor versions can break.
*   **Level 2 — Stable:** Plugin APIs, Adapter APIs, Verification Framework. Protected by semantic versioning. Deprecation requires 1 major version.
*   **Level 3 — Production:** Core capabilities, Execution Profiles. Deprecation requires 2 minor versions.
*   **Level 4 — LTS:** Server API, CLI `serve` commands. Extended support, rigorous backward compatibility.
*   **Level 5 — Core Architecture:** Internal APIs (`EnginePool`, `Scheduler`, `ExecutionEngine`). Strictly encapsulated, no external exposure guarantees.

## 2. API Versioning Strategy
Components evolve at different rates and require specific versioning guarantees:

*   **Capabilities & Execution Profiles:** Semantic Versioning (Major.Minor). Unknown minor fields are ignored; mismatched majors are rejected.
*   **Execution IR & Plans:** Protocol Versioning (v1, v2). Upward compatibility is maintained through IR translation passes.
*   **Plugins:** Strict SemVer. Manifests must explicitly declare compatible Core Runtime versions (e.g., `>=1.2.0, <2.0.0`).
*   **Adapters:** Semantic Versioning tied to Capability support.
*   **Configuration & Verification Schemas:** Schema Versioning (e.g., `schema_v1`). Upgraded via migration bridges.

## 3. Core API Ecosystem Overviews
*While specific class signatures are available via inline docstrings, the following subsystems form the public API boundary.*

*   **Runtime API (L4):** FastAPI endpoints and CLI commands providing access to generation and server state.
*   **Compiler API (L5):** Internal interfaces for `ExecutionPlanner`, `PassManager`, and `CapabilityResolver`.
*   **Backend & IR API (L5):** Interfaces defining `ExecutionIR`, `IRNode`, `Physical IR`, and backend translation protocols.
*   **Plugin & Extension API (L2):** The `PluginContext`, Event Bus (`context.on_event`), and immutable Extension Points (`ExecutionBackendExtension`).
