# RAES-012: Unified Model Adapter & Capability Resolution Architecture

## Context
The repository has established a runtime execution architecture decoupling the scheduler from execution specificities:

```
Scheduler -> GenerationStrategy -> ExecutionBackend -> ExecutionPipeline -> ExecutionEngine
```

Execution ownership has been successfully migrated away from the Scheduler.
The next architectural milestone is designing the **Model Adapter Layer**. This layer sits before execution begins. Its responsibility is to inspect a model and describe exactly how that model should execute, acting as the authoritative source of truth about a model's capabilities and operational requirements.

## Objective
Design a unified Model Adapter architecture capable of supporting current and future model families without introducing model-specific logic or heuristics throughout the runtime components (Scheduler, Profile selection, Strategies).

The design must support:
- Dense autoregressive transformers
- Vision-language models (VLMs)
- Embedding models
- Audio models
- Diffusion language models
- Nemotron Labs Diffusion
- DiffusionGemma
- Streaming MoE
- Future architectures

---

## Repository Audit

Currently, model-specific logic is scattered across various modules, often relying on fragile string matching, hardcoded lists, or heuristics:

*   **`omlx/model_discovery.py`**:
    *   Hardcoded sets like `VLM_MODEL_TYPES` and `RERANKER_ARCHITECTURES`.
    *   Heuristic-heavy `detect_model_type` looking for string markers in config fields (e.g., checking if `"diffusion"` is in `model_type` or architecture, checking for `SentenceTransformers` in `modules.json`).
    *   Template-based thinking detection in `detect_thinking_default` (matching `"enable_thinking"` vs `"default(false)"`).
    *   Hardcoded checks for context length defaults by model family.

*   **`omlx/runtime/capabilities.py` (`infer_capabilities`)**:
    *   Checks for `config.get("model_type") == "nemotron_labs_diffusion"` to infer diffusion support.
    *   Uses Python's `hasattr` to check if a loaded model object possesses specific attributes (e.g., `hasattr(model, "diffusion_head")`, `hasattr(model, "draft_model")`) to enable Diffusion or Linear Speculation capabilities.

*   **`omlx/inference/execution_profile.py` (`_default_resolver`)**:
    *   Uses hardcoded checks: `context.model_info.config_model_type in ["nemotron_labs_diffusion"]` and `["diffusion"]` to resolve to the `"experimental_nemotron"` or `"diffusion"` backend profiles.

*   **`omlx/registry/model_info.py` (`build_model_info`)**:
    *   Infers generation modes based on raw capabilities, mapping `supports_diffusion` directly to `GenerationMode.DIFFUSION` and `AttentionMode.DIFFUSION` with hardcoded priority logic.

*   **`omlx/patches/` and Custom Model Wrappers**:
    *   There is already an adapter-like concept in `omlx/models/adapters/nemotron_adapter.py` (`NemotronModelAdapter`) which wraps an MLX model to override masking. However, this is tightly coupled with the backend and not generalized.
    *   Model-specific patches (e.g., `omlx/patches/mlx_lm_mtp`, `omlx/patches/deepseek_v4`) exist outside a unified adapter flow.

*   **Model Loading (`omlx/models/llm.py`, `utils/model_loading.py`)**:
    *   Loading logic intercepts configurations (e.g., `expand_per_layer_quant_keys`) based on specific oQ tensor naming conventions.

### Documented Decisions to Change
The repository makes decisions based on configuration fields rather than explicit capability contracts. Adapters will replace these heuristics with formal declarations.

---

## Current Runtime Flow (Before Adapters)

1. **Model Directory** (`/path/to/model`)
    ↓
2. **Model Discovery** (`omlx/model_discovery.py: discover_models`)
    * Reads `config.json`, applies heuristics and string matching to guess `ModelType` (`llm`, `vlm`, `embedding`, etc.).
    ↓
3. **Config Parsing & Capability Inference** (`omlx/runtime/capabilities.py: infer_capabilities`)
    * Reads `model_type`, looks for substrings to guess capabilities (`supports_diffusion=True`).
    ↓
4. **Model Loading** (`omlx/models/llm.py`, `EngineCore`)
    * Instantiates `MLXLanguageModel`.
    ↓
5. **Context Building & Profile Selection** (`omlx/registry/model_info.py`, `omlx/inference/execution_profile.py`)
    * `build_model_info` combines inferred capabilities.
    * `ExecutionProfileRegistry` resolves the profile, currently checking `context.model_info.config_model_type` explicitly for things like `nemotron_labs_diffusion`.
    ↓
6. **Backend Selection** (`ExecutionProfileRegistry`)
    * Provides a `BackendFactory` returning an `ExecutionBackend`.
    ↓
7. **Pipeline Composition** (`ExecutionBackend.pipeline()`)
    * Constructs an `ExecutionPipeline`.
    ↓
8. **Execution Engine** (`ExecutionEngine`)
    * Instantiated (e.g., `NemotronExecutionEngine`) and invoked by the backend.

---

## Model Adapter Architecture

The Model Adapter acts as the singular translation layer between the raw model artifacts (weights, configs, tokenizers) and the OMLX runtime.

### Unified Adapter Interface (`BaseModelAdapter`)

Adapters do not inspect raw configs. Instead, Discovery produces a `ModelDescriptor` which the adapter consumes. The adapter describes its requirements via a unified `AdapterDescriptor`.

```python
@dataclass(frozen=True)
class ModelDescriptor:
    """Normalized representation of model artifacts produced by Discovery."""
    path: Path
    config: dict
    generation_config: dict
    tokenizer_config: dict

@dataclass(frozen=True)
class AdapterDescriptor:
    """Immutable definition of an adapter's capabilities and requirements."""
    identity: IdentityMetadata
    capabilities: ModelCapabilities
    execution: ExecutionMetadata
    attention: AttentionMetadata
    cache: CacheMetadata
    hardware: HardwareMetadata
    verification: VerificationMetadata

class BaseModelAdapter(Protocol):
    """Authoritative source describing a model's lifecycle and capabilities."""

    # 1. Identity & Matching
    @classmethod
    def can_adapt(cls, descriptor: ModelDescriptor) -> bool: ...

    # 2. Descriptor Resolution
    def get_descriptor(self) -> AdapterDescriptor: ...

    # 3. Lifecycle Hooks
    def pre_load(self, descriptor: ModelDescriptor) -> None: ...
    def post_load(self, model: Any) -> Any: ...
    def prepare_tokenizer(self, tokenizer: Any) -> Any: ...
    def prepare_runtime(self, context: ExecutionContext) -> None: ...
    def cleanup(self) -> None: ...

    # 4. Runtime Behavior
    def create_attention_mask(self, q_len: int, prefix_len: int, context: dict) -> Any: ...
```

### Traits Composability

Adapters are organized by execution family (e.g., `AutoregressiveAdapter`), not by narrow model type. Capabilities like Vision or MoE are mixed in using **Traits**:

```python
class Qwen2VLAdapter(AutoregressiveAdapter, VisionTrait, MoETrait):
    # Combines baseline AR execution with Vision-specific preprocessing and MoE routing logic.
    pass
```

### Adapter Responsibilities

Based on repository evidence, the following belong *inside* the adapter:
*   **architecture metadata**: Adapters declare if a model is MoE, Diffusion, or AR.
*   **attention metadata**: Adapters define custom mask generation (like `NemotronModelAdapter.create_diffusion_mask`).
*   **capability inference**: Resolving if speculative decoding or bidirectional attention is needed.
*   **tokenizer metadata hints**: e.g., default thinking suppression templates.
*   **kernel hints**: Declaring if a custom C++ kernel (e.g., `omlx/custom_kernels/glm_moe_dsa`) should be targeted.

The following *do not* belong in the adapter:
*   **scheduler assumptions**: The scheduler remains generic. The adapter only informs it via standard capability flags.
*   **batching metadata**: Handled by the Engine/Scheduler based on memory limits, not the model.

---

## Capability Resolution

The runtime should **never guess**. Capabilities are explicitly assembled by the adapter using normalized inputs.

```
Model Directory
   ↓
[ Model Discovery normalizes artifacts ]
   ↓
ModelDescriptor (config, generation_config, tokenizer_config)
   ↓
[ Adapter.get_descriptor() ]
   ↓
AdapterDescriptor (Contains explicit ModelCapabilities)
```

## Execution Mode Resolution

Adapters map their internal architecture to standardized execution paths:

**Mapping Flow:**
1. **Adapter** returns `preferred_mode` (e.g., `GenerationMode.DIFFUSION`) and `capabilities`.
2. **ExecutionProfileRegistry** matches `GenerationMode` to a backend profile dynamically (no model strings).
3. **GenerationStrategyRegistry** (`CapabilityBundle`) matches `GenerationMode` to a strategy (e.g., `DiffusionStrategy`).
4. **BackendFactory** instantiates `ExperimentalNemotronBackend` which provides `NemotronDiffusionPipeline` and `NemotronExecutionEngine`.

**Supported Modes:**
*   **Autoregressive**: Handled by `AutoregressiveStrategy` -> `AutoregressiveBackend`
*   **Diffusion**: Handled by `DiffusionStrategy` -> `ExperimentalNemotronBackend` (or future standard backend)
*   **Streaming MoE**: Adapter requests custom MoE kernel execution backend.
*   **Vision / Audio / Embedding**: Adapter maps to VLM/Embedding execution pipelines without hardcoded VLM type sets.

---

## Adapter Registry

A global registration mechanism prevents hardcoded switch statements during discovery.

```python
# omlx/adapters/registry.py
class AdapterRegistry:
    def __init__(self):
        self._adapters: list[type[BaseModelAdapter]] = []

    def register(self, adapter_cls: type[BaseModelAdapter]):
        self._adapters.insert(0, adapter_cls) # LIFO priority

    def resolve_adapter(self, descriptor: ModelDescriptor) -> type[BaseModelAdapter]:
        for adapter in self._adapters:
            if adapter.can_adapt(descriptor):
                return adapter
        return DefaultAutoregressiveAdapter
```

## Future Compatibility

This architecture supports future integrations purely by adding a new adapter class:

*   **Nemotron Triage**: Exists via a `TriageTrait` composed with an adapter, declaring `GenerationMode.TRIAGE` support and custom scoring requirements without impacting default execution.
*   **Nemotron Labs Diffusion**: Exists via `NemotronAdapter` returning `GenerationMode.DIFFUSION` and providing custom block masking.
*   **DiffusionGemma / Refinement Loop**: `DiffusionGemmaAdapter` requests `GenerationMode.DIFFUSION` but returns different `CacheRequirements` and `AttentionMode.BIDIRECTIONAL`. The `DiffusionStrategy` and pipelines handle the execution; the scheduler remains untouched.
*   **Streaming MoE**: `StreamingMoEAdapter` requests standard autoregressive generation but wraps the model to replace standard MLX layers with custom MoE kernels.

---

## Runtime Contracts

*   **Adapter**: Sole authority on model capabilities and structural requirements. Does not orchestrate inference.
*   **Capability Resolution**: Uses the chosen adapter to output an immutable `ModelCapabilities` bundle.
*   **Execution Profile**: Resolves `ModelCapabilities` to an `ExecutionBackend`. Knows *nothing* about model architectures.
*   **Strategy**: Implements generation logic (AR, Diffusion) using backend primitives.
*   **Backend / Pipeline / Engine**: Executes mathematical operations for a specific profile.

---

## Repository Changes

**New Files:**
*   `omlx/adapters/base.py`: Defines `BaseModelAdapter` Protocol.
*   `omlx/adapters/registry.py`: Defines `AdapterRegistry`.
*   `omlx/adapters/implementations/`: Directory for `default_llm.py`, `nemotron.py`, etc.

**Modified Files (Exposing Interfaces):**
*   `omlx/model_discovery.py`: Replace heuristic string matching with a call to `AdapterRegistry.get_adapter()`.
*   `omlx/runtime/capabilities.py`: Refactor `infer_capabilities` to defer to the resolved Adapter instance.
*   `omlx/registry/model_info.py`: Populate from Adapter outputs rather than heuristics.
*   `omlx/inference/execution_profile.py`: Remove `config_model_type` checks in `_default_resolver`. Resolve based purely on `ModelCapabilities`.

**Untouched Files (Strict Boundaries):**
*   `omlx/scheduler.py`
*   `omlx/inference/strategies/*.py`
*   `omlx/engine_core.py`

---

## Risks

1.  **Adapter Explosion**: Every model requiring a distinct adapter leads to bloat.
    *   *Mitigation*: Provide a robust `DefaultAutoregressiveAdapter` that leverages standard HF configs. Only models with fundamental architectural deviations (Diffusion, custom MoE) require custom adapters.
2.  **Compatibility with MLX-LM**: Wrappers might interfere with upstream `mlx_lm.load` assumptions.
    *   *Mitigation*: Adapters should act on the config *before* load for capabilities, and apply lightweight proxy wrappers *after* load (as seen in `NemotronModelAdapter`) to avoid deep monkey-patching.
3.  **Configuration Drift**: Remote models change config schemas.
    *   *Mitigation*: Adapter `can_adapt` logic must be defensive and fallback to defaults gracefully.

---

## Verification Plan

1.  **Unit Tests (Adapter Selection)**: Feed mock configs (Llama, Nemotron, Gemma) to the `AdapterRegistry` and assert the correct adapter type is resolved.
2.  **Capability Inference Validation**: Assert that `NemotronAdapter.resolve_capabilities()` yields exactly `supports_diffusion=True, supports_autoregressive=False`.
3.  **Execution Mode Resolution Tests**: Ensure `ExecutionProfileRegistry` resolves the Diffusion Backend *only* when `ModelCapabilities` flags diffusion, independent of model name.
4.  **Regression Protection**: Run existing E2E test suites on standard AR models ensuring the `DefaultAutoregressiveAdapter` behaves identically to the old heuristic flow.

## Implementation Recommendation

Proceed with Phase 1: Define `BaseModelAdapter` and `AdapterRegistry`. Port the existing heuristics for `detect_model_type` into `DefaultAutoregressiveAdapter` and `DefaultVLMAdapter`, and convert the existing `NemotronModelAdapter` to this new interface.
This introduces the pattern safely without modifying runtime behavior.

## Rollback Strategy
If the implementation introduces critical regressions (e.g. failing to resolve capabilities or correctly configure an execution profile), we will safely rollback:
1. Revert modifications in `omlx/model_discovery.py` to restore the original string-matching and heuristic-based checks.
2. Revert modifications to `omlx/runtime/capabilities.py` back to `infer_capabilities` using `config.get` checks.
3. Keep the `adapters/` directory and registry in the codebase, but disabled by default.

## Diagrams
### Runtime Ownership
```
Model Config -> Adapter -> Capability Resolution -> Execution Profile -> Execution Backend -> Engine -> Run Step -> Metrics
```

### Future Model Integration
```
Future Architecture -> Model Discovery -> Custom Adapter (e.g., StreamingMoEAdapter) -> Registry -> Capability Assembly -> Execution Path -> Custom Pipeline
```
