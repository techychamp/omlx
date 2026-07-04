# Model Adapter Architecture Plan

## Executive Summary

This document outlines the architectural plan for introducing a Model Adapter Architecture into oMLX. The primary goal is to decouple model-specific quirks, monkey patches, and lifecycle management from the generic runtime (`ExecutionEngine`, `ExecutionBackend`, `Scheduler`, `EngineCore`). The new design supports future model families (Diffusion, Streaming MoE, Verification) without requiring invasive changes to the core scheduling or execution loop.

## 1. Repository Audit: Current State

Our audit of the codebase reveals model-specific logic leaked into several layers:

1. **Monkey Patches (`omlx/patches/`)**:
   - `maybe_apply_pre_load_patches` in `omlx/utils/model_loading.py` dispatches model-specific pre-load patches (e.g., DeepSeek V4, Llama 4, GLM DSA, Step 3.7).
   - Patches are deeply tied to `config.json` `model_type` values.

2. **Engines (`omlx/engine/`)**:
   - `BatchedEngine`, `DFlashEngine`, `VLMBatchedEngine` have hardcoded checks for `model_type` strings to toggle features (e.g., `model_type == "gemma4"`, `is_qwen`, etc.).
   - Modality mapping and hardware capability toggles are hardcoded in engine classes.
   - Specific VLM prompt engineering rules, chat template overrides, and image processing constraints exist in `vlm.py`.

3. **Inference Pipeline (`omlx/inference/`)**:
   - Specific model properties are currently exposed or leaked to pipeline construction.

4. **Configuration & Capabilities**:
   - Architecture detection and STS family mapping are hardcoded in `sts.py` and `api/utils.py`.

**Inventory of areas to extract to adapters**:
- Model loading hook pre/post initialization
- Architecture detection and configuration validation
- Tokenizer preparation and quirks
- RoPE scaling logic and overrides
- Attention mask generation rules (e.g., block masks, streaming)
- KV cache layout specifications
- Expert routing/Streaming MoE constraints
- Chat template quirks and image/audio token handling
- Hardware/optimizations hints

## 2. Adapter Architecture

### Design Philosophy

The runtime components (`Scheduler`, `EngineCore`, `ExecutionBackend`, `ExecutionEngine`) will remain untouched. Instead, models will be managed by an Adapter architecture designed around **execution behavior** and **composition**, rather than a rigid taxonomy of model types.

### Adapter Hierarchy: Behavior & Traits

Adapters are organized around foundational execution behaviors rather than model taxonomy. Capabilities like Vision or MoE are mixed in as composable traits rather than top-level adapter classes.

```text
BaseAdapter
        │
        ├──────── AutoregressiveAdapter
        │
        ├──────── DiffusionAdapter
        │
        ├──────── VerificationAdapter
        │
        ├──────── EmbeddingAdapter
        │
        └──────── EncoderAdapter
```

**Composition and Traits**:
Instead of creating a `VisionMoEAdapter`, an autoregressive VLM with MoE layers would be represented as:
`AutoregressiveAdapter` + `VisionTrait` + `MoETrait`.
This highly scalable composition allows traits to handle specialized tokenizer rules or visual block masks independently of the primary execution mode.

### Lifecycle Phases

To prevent adapters from becoming bloated "god classes," the adapter contract is split into distinct lifecycle phases:

1. **Discovery Phase**: Analyzes the model directory to identify required traits, capabilities, and execution family.
2. **Configuration Phase**: Cleans, parses, and normalizes `config.json` into a standardized format.
3. **Loading Phase**: Handles the execution of patches, instantiates the model object, and loads weights.
4. **Runtime Phase**: Prepares tokenizers, builds attention masks, provides chat templates, and supports forward-pass metadata.
5. **Cleanup Phase**: Safely tears down resources, unloads context, and cleans up references.

### Structured Descriptors (Metadata vs. Behavior)

Instead of querying dozens of independent methods (e.g., `get_execution_hints()`), adapters expose a structured descriptor that defines exactly what the model is and what it needs.

**AdapterDescriptor**:
- `CapabilityDescriptor`: High-level traits (e.g., Vision, MoE).
- `ExecutionHints`: Optimization flags, parallelization strategies.
- `HardwareRequirements`: Memory bounds, required accelerator features.
- `VerificationProfile`: Golden prompts, expected tolerances.
- `PatchRequirements`: Declares which patches must be applied.

## 3. Patch Pipeline Plugins

Monkey patches will no longer be monolithic `maybe_apply_...` functions. Instead, patches become isolated, reusable adapter plugins.

**Execution Flow**:
`Adapter` → `Patch Pipeline` → `[Patch 1, Patch 2, ...]`

Adapters declare a list of required `PatchRequirements` in their descriptor. The Patch Pipeline executes them sequentially during the Loading phase. This isolates side effects, makes patches reusable across adapters (e.g., `SDPAPatch`, `Llama4RoPEPatch`), and dramatically simplifies testing.

## 4. Execution Graph Metadata

Adapters will act as the source of truth for the execution planner. Instead of the backend trying to infer what to build, the adapter provides explicit execution graph metadata:

- `ExecutionGraphType` (e.g., single-pass, recurrent)
- `CacheLayout` (e.g., paged KV, rotating, block-sparse)
- `AttentionType` (e.g., dense, sliding window, native MTP)
- `SamplingType` (e.g., greedy, speculative, rejection)
- `VerificationStages` (e.g., draft, verify, correct)
- `ExecutionFamily`

## 5. Interaction with Runtime

Long term, the explicit `AdapterFactory` will be phased out in favor of integration with the Capability Resolver.

**Component Resolution Flow**:
`Model Discovery` → `Capability Resolver` → `Execution Planner` → `Adapter Resolver` → `Adapter Instantiation`

This turns the Adapter into just another resolved component in the pipeline, completely decoupling model loading from the execution loop.

## 6. Future Execution Families Integration

The design cleanly isolates future functionality:

- **Nemotron Labs Diffusion / DiffusionGemma**: Implemented via `DiffusionAdapter`. Uses a `DiffusionTrait` to inject required iterative denoising metadata and block masks.
- **Nemotron Triage**: Implemented via `VerificationAdapter` using draft generation and verification stage traits.
- **Streaming MoE**: An `MoETrait` applied to an `AutoregressiveAdapter` handles expert routing and partial loading cache hints.

## 7. Interaction with Verification Framework

Adapters will expose their verification metadata interface through the `VerificationProfile` inside the `AdapterDescriptor`.
This automatically supplies `verification_framework.md` with:
- Golden prompts and HF equivalency targets.
- Precision tolerances.
- Cache comparison metrics.

## 8. Risk Analysis

1. **Trait Combinatorics**: Overlapping traits could conflict. *Mitigation*: Traits must be scoped strictly to their domain (e.g., VisionTrait only handles image inputs).
2. **Patch Unloading**: Modifying global state is risky. *Mitigation*: The Patch Pipeline must track applied patches and ideally support a rollback mechanism or restrict application to isolated processes.
3. **Execution Graph Complexity**: Exposing graph definitions from the adapter may couple it too tightly to the backend. *Mitigation*: Adapters emit declarative enum/dataclass hints, not actual execution logic.

## 9. Verification Plan (No Implementation)

- **Phase Isolation Test**: Ensure Configuration phase can be run independently of Loading phase.
- **Descriptor Verification**: Validate `AdapterDescriptor` payload structure matches strict schemas.
- **Patch Pipeline Test**: Verify isolated patch plugins can be applied and verified without loading a full model.
- **Resolver Flow Test**: Mock the `Adapter Resolver` to verify it correctly outputs an `AutoregressiveAdapter` with `VisionTrait` for a mock VLM.

## 10. Files to Modify / Create

**NEW**:
- `omlx/adapter/base.py`: Defines lifecycle interfaces and structured descriptors.
- `omlx/adapter/behaviors.py`: Defines `AutoregressiveAdapter`, `DiffusionAdapter`, etc.
- `omlx/adapter/traits.py`: Defines `VisionTrait`, `MoETrait`, etc.
- `omlx/adapter/plugins/`: Directory for isolated patch plugins.
- `omlx/adapter/resolver.py`: The `Adapter Resolver` component.

**MODIFIED**:
- `omlx/utils/model_loading.py`: Deprecate `maybe_apply_pre_load_patches` in favor of the adapter Patch Pipeline.
- `omlx/engine_pool.py`: Use `Adapter Resolver` to construct the adapter and read its descriptor.

**UNTOUCHED**:
- `Scheduler`
- `ExecutionBackend`
- `ExecutionEngine`
- `Server`

## 11. Recommendation for Next Checkpoint
The next checkpoint should focus on implementing the lifecycle interface (`BaseAdapter`), the structured `AdapterDescriptor`, and the `Patch Pipeline`. We should port one simple model (e.g., standard dense autoregressive) to validate the resolver and patching behavior before addressing traits like Vision or MoE.

## 12. Rollback Strategy

**Strategy**:
1. **Side-by-Side Implementation**: The `Adapter Resolver` will be introduced alongside existing legacy `load_text_model` and patch logic.
2. **Feature Flagging**: The migration will be gated behind an environment variable (e.g., `OMLX_USE_ADAPTERS=1`). If absent, the system falls back to the legacy string-based checks.
3. **Incremental Migration**: Models will be migrated to the new behavior+traits system one family at a time.
4. **Fast Revert**: If an adapter causes regression in production, removing it from the `Adapter Resolver` registry will instantly revert that model type to the legacy codepath.
