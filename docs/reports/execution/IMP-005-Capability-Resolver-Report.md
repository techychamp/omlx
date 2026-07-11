# Capability Resolver Audit Report

## 1. Existing Capability Detection
Currently, capabilities are detected in a scattershot manner across multiple files:
- `omlx/registry/capability_registry.py` defines generic capabilities but relies on external `ActualCapabilities`.
- `omlx/model_discovery.py` uses hardcoded heuristics on `config.json` to deduce capabilities (e.g. VLM vs Autoregressive).
- `omlx/inference/execution_profile.py` hardcodes checking model type against known features.

## 2. Model Type & Architecture Detection
Model type and architecture checks are widespread:
- Heavy use of `getattr(config, "model_type", None)` inside patches (`omlx/patches/*`).
- Specialized checks in `omlx/patches/index_cache.py`, `omlx/adapter/output_parser.py`, and specific model extensions.

## 3. Feature Detection
Features are often deduced inline:
- Streaming support, sliding window attention, or specific memory layouts are derived directly during execution setup or via patches checking config blocks.

## 4. Execution Profile Selection
Profile selection in `omlx/model_settings.py` merges `model_id` specific JSON settings overrides manually.

## 5. Summary
The absence of a centralized `CapabilityResolver` results in components (planners, adapters, UI) performing isolated configuration lookups and raw dictionary inspections. The planned module `omlx/capabilities/` will normalize these streams into a single `CapabilityDescriptor` evaluated deterministically.

## 6. Architecture Report
The `CapabilityResolver` acts as the single authoritative component for evaluating and merging capabilities.
- It uses a modular `CapabilitySource` interface, allowing multiple inputs (`ModelMetadataSource`, `FeatureFlagSource`, `RuntimeOverrideSource`, `PluginSource`) to be registered and evaluated.
- A deterministic merge priority was established and implemented in `omlx/capabilities/merge.py`.
- Final outputs are encapsulated in a frozen, immutable dataclass `CapabilityDescriptor` from `omlx/capabilities/descriptor.py`.
- Validation is enforced in `omlx/capabilities/validation.py`, blocking incompatible states (e.g. `ExecutionFamily.DIFFUSION` alongside `supports_streaming=True`).

## 7. Merge Precedence
The implementation establishes the following merge priority (from lowest priority to highest priority, i.e. later rules overwrite earlier rules):
1. Defaults (Implicit fallback inside descriptor)
2. Model metadata (from JSON definitions)
3. Adapter metadata (via plugin configs)
4. Plugins (Dynamic injections)
5. Feature Flags (Overrides from configuration)
6. Runtime overrides (Execution profile explicit overwrites)

## 8. Capability Lifecycle
1. `CapabilityResolver` is initialized with default sources inside `RuntimeBuilder`.
2. As a model context resolves, `CapabilityResolver.resolve(model_descriptor, additional_sources)` is called.
3. Capabilities are mapped, validated, and normalized into `CapabilityDescriptor`.
4. The descriptor is safely shared (being an immutable frozen dataclass) with the EnginePool, Planners, and UI Metadata.

## 9. Validation Report
The `CapabilityResolver` ensures semantic correctness by raising `CapabilityValidationError` if conflicting metadata is detected.
Examples:
- Autoregressive models attempting to use Diffusion-style Attention.
- Diffusion or Embedding models claiming to support Streaming inference.

## 10. Repository Impact Report
- `omlx/capabilities/` was created, encapsulating the entire subsystem cleanly.
- `omlx/runtime/builder.py` updated to include `CapabilityResolver` inside `RuntimeContext` matching the Composition Root architecture.
- Replaces future hardcoded JSON dictionary lookups across Model Discovery.

## 11. Future EventBus Integration
Currently, the resolver operates synchronously without depending on `EventBus`.
When EventBus (IMP-004) is implemented:
- `CapabilityResolver.resolve()` should optionally publish a `CapabilityResolved` event.
- This allows passive plugins (e.g., memory profilers or observability hooks) to react whenever a new `CapabilityDescriptor` is baked.

## 12. Rollback Procedure
If `CapabilityResolver` introduces bugs:
1. Revert modifications in `omlx/runtime/builder.py` (removing `capability_resolver` injection).
2. The core system still references legacy dictionary parsing, making rollback transparent.

## 13. Recommendations for IMP-006
IMP-006 should leverage the `CapabilityDescriptor` inside the **Execution Planner**.
- The Planner should stop reading `config.json` manually and instead consume the `CapabilityDescriptor` to deduce whether to instantiate an `AutoregressiveStrategy` or a `DiffusionStrategy`.
- Adapters should be updated to contribute a `CapabilitySource` rather than patching dictionaries directly.
