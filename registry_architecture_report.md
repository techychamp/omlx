# Registry Architecture Report (IMP-003)

## Current State Audit

### execution_profile.py
- Currently owns `ExecutionProfileRegistry` as a global singleton (`_GLOBAL_PROFILE_REGISTRY`).
- Maps `ExecutionContext` to `ExecutionProfile` and `BackendFactory`.
- Has hardcoded factory functions (e.g., `_autoregressive_factory`).
- Resolvers use basic if/else statements for model types.

### model_settings.py
- Handles per-model settings.
- Manages profiles like `MODEL_SPECIFIC_PROFILE_FIELDS`.
- Uses a file-based JSON storage mechanism to persist settings.
- Manages hardcoded versions for formats (`SETTINGS_VERSION`, `PROFILES_VERSION`).

### model_discovery.py
- Hardcodes a map of model types to engine types (`BatchedEngine`, `VLMBatchedEngine`, etc.).
- Direct instantiation and estimation of memory limits.
- Model discovery metadata is tied directly to engine instantiation logic.

### engine_pool.py
- Global `ModelRegistry` (in `model_registry.py`) tracks which engines own which model.
- Ownership is tracked via weakrefs in a lock-protected dictionary.
- Does not strictly isolate metadata from runtime (ties directly to `EngineCore` and model references).

### Plugin Loading
- `plugin_discovery.py` defines basic entry point discovery using `pkg_resources`.
- No central structured metadata registry for plugins beyond entry points.

### Verification Framework
- Verification rules and compatibility currently scattered.
- No structured verification profile or compatibility capability metadata.

## Future Migration Targets

The new `GenericRegistry` will provide a unified metadata backbone:

1. **CapabilityRegistry / ExecutionModeRegistry**:
   - Replaces `GenerationStrategyRegistry` in `capability_registry.py`.
   - Capabilities become structured, JSON-serializable entries instead of dataclass bundles with hardcoded logic.
2. **ExecutionProfileRegistry**:
   - Replaces `ExecutionProfileRegistry` in `execution_profile.py`.
   - Will serialize profiles to JSON and use immutable, locked states instead of global singletons.
3. **AdapterRegistry**:
   - Will store metadata for adapters separate from execution logic.
4. **BackendRegistry**:
   - Will decouple backend metadata from factory functions.
5. **PluginRegistry**:
   - Will formalize plugin metadata loading from entry points.
6. **VerificationRegistry**:
   - Will centralize validation profiles.

The integration into `RuntimeBuilder` (IMP-002) ensures these registries are instantiated per-runtime, locked before startup, and serve purely as immutable metadata sources.
