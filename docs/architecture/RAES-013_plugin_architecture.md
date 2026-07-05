# RAES-013 — Plugin & Extension Architecture

## 1. Repository Audit

An audit of the current `omlx` repository reveals several mechanisms designed to decouple core runtime capabilities from specific model implementations or execution strategies.

### Existing Extension Points & Registries

1.  **Plugin Discovery (`omlx/registry/plugin_discovery.py`)**
    *   **Mechanism:** Uses standard Python `importlib.metadata.entry_points`.
    *   **Group:** `omlx.strategies`
    *   **Functionality:** Looks for entry points pointing to functions that accept a `GenerationStrategyRegistry` and register their capability bundles.

2.  **Generation Strategy Registry (`omlx/registry/capability_registry.py`)**
    *   **Mechanism:** `GenerationStrategyRegistry` (instantiated per-engine, not as a global singleton).
    *   **Functionality:** Maps `GenerationMode` (e.g., `AUTOREGRESSIVE`, `DIFFUSION`, `LINEAR_SPECULATION`) to a `CapabilityBundle`.
    *   **Bundle Contents:** Contains `strategy_class`, `attention_modes`, `cache_hints`, `scheduler_hooks`, and `ui_metadata`.

3.  **Execution Profile Registry (`omlx/inference/execution_profile.py`)**
    *   **Mechanism:** `ExecutionProfileRegistry` with a global instance `_GLOBAL_PROFILE_REGISTRY`.
    *   **Functionality:** Resolves an `ExecutionContext` (ModelInfo, EngineCapabilities, FeatureFlags) into an `ExecutionProfile`. Uses registered resolver functions. Also maps backend names (e.g., `autoregressive`, `experimental_nemotron`) to `BackendFactory` callables.

4.  **Execution Backend & Pipeline (`omlx/inference/execution_backend.py`, `omlx/inference/execution_graph.py`)**
    *   **Mechanism:** `ExecutionBackend` protocol mapping to `ExecutionEngine`. `ExecutionPipeline` composed of `ExecutionStage` instances.
    *   **Graph:** `ExecutionGraph` defines abstract nodes (Prefill, Forward, Sample, Verify, Denoise) pointing to next nodes, guiding the strategy flow.

5.  **API Adapters (`omlx/api/adapters/`)**
    *   **Mechanism:** Classes inheriting from `BaseAdapter` converting specific API formats (OpenAI, Anthropic) to internal representations (`InternalRequest`, `InternalResponse`).

6.  **Custom Kernels (`omlx/custom_kernels/`)**
    *   **Mechanism:** Optional native metal kernels (e.g., `glm_moe_dsa`, `minimax_m3`) bound to python via `fast.py` modules. Patched into execution using dispatch objects.

### Limitations of Current State
*   **Decentralized Registration:** Registration logic is split across `get_profile_registry().register_backend()`, entry points targeting `GenerationStrategyRegistry`, and hardcoded adapter resolution.
*   **Missing Dependency Management:** Entry points load plugins, but there is no mechanism to guarantee that a strategy plugin's required backend or capabilities are present.
*   **Static Context:** Adapters and models are implicitly loaded. Adding a totally new model family with a custom architecture requires touching core model resolution code.

## 2. Existing Extension Architecture

Based on repository evidence, the current extension flow is:

```text
Plugin (via setuptools entry points `omlx.strategies`)
  ↓
importlib.metadata reads entry points
  ↓
Plugin Init Function called with `GenerationStrategyRegistry`
  ↓
Registers `CapabilityBundle` (associates Mode with Strategy)
```

At runtime, for a specific request/model:

```text
Model Details + Capabilities -> `ExecutionContext`
  ↓
`ExecutionProfileRegistry` resolves Context to `ExecutionProfile`
  ↓
`ExecutionProfile` maps to `BackendFactory`
  ↓
Factory creates `ExecutionBackend` (containing Engine & Pipeline)
  ↓
Request mode maps to `BaseGenerationStrategy` (via `GenerationStrategyRegistry`)
  ↓
Strategy executes using Backend / Pipeline / Graph
```

## 3. Plugin Taxonomy

Plugins in `omlx` should be categorized to control interface boundaries and registration expectations. All categories belong in the repository as abstract plugin interfaces, though implementations may live externally.

1.  **Model Plugins:** Implement `ModelInfo`, standard HuggingFace config parsing, and standard architecture forwarding (if custom). Examples: `Llama`, `Gemma`, `Nemotron`, `DeepSeek`.
2.  **Execution Plugins:** Implement `ExecutionBackend`, `ExecutionPipeline`, `ExecutionStage`, `ExecutionGraph`. Examples: `AutoregressiveBackend`, `ExperimentalNemotronBackend`.
3.  **Strategy/Capability Plugins:** Implement `BaseGenerationStrategy` or inject into capability registries to handle novel generation loops (e.g., streaming MoE, diffusion denoising, triage).
4.  **Kernel Plugins:** Provide optimized Metal/C++ kernels mapping to Python APIs.
5.  **Adapter Plugins:** Implement `BaseAdapter` for custom API surfaces.
6.  **Runtime Hooks / Verifiers:** Implement logging, benchmarking, monitoring, or HF equivalence checks.

## 4. Plugin Lifecycle

1.  **Discovery:** `importlib.metadata` scans entry points (e.g., `omlx.plugins`).
2.  **Validation:** `plugin_loader.py` instantiates the plugin class/function and validates its `PluginManifest` (checking version and required fields).
3.  **Dependency Resolution:** The plugin manager ensures all dependencies defined in the manifest are present and activated. If not, the plugin is skipped or errors out gracefully.
4.  **Registration:** The plugin's `register(context: PluginContext)` method is called, passing registries (Strategy, Profile, Adapters).
5.  **Activation/Initialization:** Plugins initialize heavy dependencies (e.g., compiling JIT kernels).
6.  **Runtime Usage:** The core runtime uses registered components seamlessly.
7.  **Shutdown:** `teardown()` hooks are called on registered components on server exit.

## 5. Registration Design

Instead of having plugins import global singletons (which break test isolation and per-engine scoping), plugins should be given a `PluginContext` to register their components.

```python
# Conceptual interface
class PluginContext:
    def register_backend(self, name: str, factory: BackendFactory): ...
    def register_strategy(self, bundle: CapabilityBundle): ...
    def register_adapter(self, name: str, adapter_cls: Type[BaseAdapter]): ...
    def register_profile_resolver(self, resolver: Callable): ...
    def register_execution_graph(self, graph: ExecutionGraph): ...
    def register_optimization_pass(self, name: str, opt_pass: Any): ...
    def register_verification_pass(self, name: str, ver_pass: Any): ...
    def register_execution_ir_node(self, node_type: str, node_cls: Any): ...
    def register_analysis_pass(self, name: str, analysis_pass: Any): ...
```

This centralizes extension into a single lifecycle hook, ensuring all components adhere to the OMLX platform contracts without altering internal logic.

## 6. Dependency Resolution

Plugins must declare dependencies to ensure safe loading.

*   **Mechanism:** `PluginManifest` specifies required plugins by name and version (e.g., `>=1.0`).
*   **Resolution:** A DAG (Directed Acyclic Graph) of plugin dependencies is constructed during the Discovery phase.
*   **Conflicts:** If two plugins require incompatible versions of a base plugin, or if a cycle is detected, the runtime refuses to load the conflicting extensions and degrades gracefully (logging an error but continuing with base functionality).

## 7. Plugin Manifest

To facilitate validation and dependency resolution, plugins will provide a manifest.

```python
@dataclass
class PluginManifest:
    name: str                       # e.g., "omlx-nemotron"
    version: str                    # e.g., "1.0.0"
    author: str
    provides: set[str]              # e.g., {"diffusion"}
    requires: set[str]              # e.g., {"metal"}
    extends: set[str]               # e.g., {"autoregressive"}
```

## 8. Runtime Context

During registration, plugins receive a `PluginContext`. During execution, injected components (Strategies, Backends) receive `ExecutionContext` and `ExecutionRuntime` (which already exist in the codebase).

**Exposed to Plugins at Registration (`PluginContext`):**
*   Registries (Profiles, Strategies, Adapters, Kernels)
*   Global Feature Flags

**Exposed to Plugins at Execution (`ExecutionContext` / `ExecutionRuntime`):**
*   Model Metadata (`ModelInfo`)
*   Engine Capabilities
*   Hardware Info (available memory, active GPU stream)

**Not Exposed:**
*   Scheduler internal queues.
*   Engine internal state management.
*   Raw pointer addresses unless via defined MLX array APIs.

## 9. Third-Party Extension Design

External packages can safely extend OMLX using pip and Python entry points.

1.  User runs `pip install omlx-nemotron` (a third-party PyPI package).
2.  `omlx-nemotron` defines `[project.entry-points."omlx.plugins"]` in its `pyproject.toml`.
3.  On server start, `omlx` discovers the entry point.
4.  OMLX verifies the manifest and resolves dependencies.
5.  The plugin registers `ExperimentalNemotronBackend` and `DiffusionStrategy` via `PluginContext`.
6.  When the user requests a Nemotron model, the `ExecutionProfileRegistry` (augmented by the plugin) resolves it to the new backend.
7.  The runtime executes it without ever touching core engine/scheduler code.

## 10. Repository Changes

**New Files (Minimal Addition):**
*   `omlx/registry/plugin_contract.py` (Defines `PluginManifest`, `PluginContext`, and `OMLXPlugin` protocol)
*   `omlx/registry/plugin_manager.py` (Handles DAG resolution and manifest validation, wrapping existing `plugin_discovery.py`)

**Modified Files (To expose interfaces):**
*   `omlx/registry/plugin_discovery.py` (Update to use `plugin_manager.py` and `PluginManifest`)

**Untouched Files (Core stability):**
*   `omlx/inference/execution_engine.py` (Must remain unaware of plugins)
*   `omlx/scheduler/*.py` (Scheduling is strictly decoupled)
*   `omlx/server/*.py` (FastAPI routes remain identical)

## 11. Security Analysis

*   **Plugin Isolation:** Currently, plugins run in the same Python process. Long-term, the architecture must consider isolation mechanisms such as `PluginProcess` or `SubprocessWorker` for experimental kernels. This is not strictly because Python plugins are unsafe, but because a native MLX core crash will bring down the entire process. A multiprocess architecture insulates the main server from experimental memory faults.
*   **Validation:** Manifests are type-checked. Registration methods enforce `Protocol` checks.
*   **Runtime Failures:** If a plugin's backend crashes, the specific request fails, but the global exception handlers in the FastAPI layer prevent the server from crashing.
*   **Graceful Degradation:** A failed plugin load does not prevent OMLX from starting, unless the user explicitly flags the plugin as strictly required.

## 12. Verification Plan

The following test suites must be developed in `tests/registry/test_plugin_architecture.py`:
1.  **Discovery:** Mock entry points to ensure plugins are discovered.
2.  **Registration:** Verify that using `PluginContext.register_*` correctly mutates the underlying registries.
3.  **Dependency Resolution:** Create a mock DAG of plugins and verify correct topological load order. Ensure cycles raise appropriate, caught exceptions.
4.  **Version Conflicts:** Test manifest version specifiers against installed plugin versions.
5.  **Runtime Activation:** End-to-end test with a dummy plugin to ensure a mocked request routes to the plugin's custom backend.
6.  **Graceful Failure:** Ensure a plugin that raises an exception during `register()` does not halt the entire discovery process.

## 13. Rollback Strategy

Because this architecture builds upon existing abstractions (`GenerationStrategyRegistry`, `ExecutionProfileRegistry`), it does not require breaking changes to existing built-in models. If the `plugin_manager.py` logic fails, the fallback is the current static initialization (which registers `autoregressive`, `diffusion`, etc. explicitly at startup). Built-in models will not depend on the dynamic discovery system to function.


## 15. Event Hooks (Future Expansion)

Eventually, plugins may need to interact with the runtime at distinct points in the request lifecycle rather than just registering static classes. The architecture should anticipate supporting:

*   **Before Discovery:** Hooks executed before the model graph is fully discovered.
*   **Before Planning:** Hooks altering the execution plan based on the request (e.g., triage overrides).
*   **Before Execution:** Hooks executing immediately before `engine.execute_cycle()`.
*   **After Execution:** Hooks for custom metric collection, cache updates, or logging.
*   **Shutdown:** Safe teardown of external resources or worker processes.

## 14. Recommendation for implementation checkpoint

The architectural primitives already exist.

**Next Immediate Steps (Implementation Checkpoint 1):**
1.  Introduce `PluginManifest` and `PluginContext` in `omlx/registry/plugin_contract.py`.
2.  Refactor `omlx/registry/plugin_discovery.py` to process manifests and inject `PluginContext` instead of just passing the strategy registry.
3.  Implement DAG resolution for dependencies.
4.  Update existing experimental plugins (e.g., `diffusion_backend`) to use the new `PluginContext` registration pattern as a proof of concept.
