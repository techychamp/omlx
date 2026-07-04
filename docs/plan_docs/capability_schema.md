# D1.1 & D1.2: Capability Schema

This document details the first two components of the capability-driven runtime: the **Runtime Capability Descriptor** (declaring model attributes and hardware requirements) and the **Capability Registry** (defining validation, defaults, and parameter semantics).

---

## D1.1: Runtime Capability Descriptor

The **Runtime Capability Descriptor** is a metadata structure resolved during the model discovery phase (e.g., in `model_discovery.py` or post-load inspection). It represents the raw capabilities supported by the model architecture combined with its operational and platform prerequisites.

### Schema Representation (JSON)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RuntimeCapabilityDescriptor",
  "type": "object",
  "properties": {
    "model_id": {
      "type": "string",
      "description": "Unique identifier of the discovered model directory"
    },
    "supported_capabilities": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of capability identifiers the model supports (e.g., 'autoregressive', 'diffusion', 'triage', 'streaming_moe')"
    },
    "platform_requirements": {
      "type": "object",
      "description": "Hardware and system constraints required to execute the model",
      "properties": {
        "min_unified_memory_gb": { "type": "integer" },
        "requires_bidirectional_attention": { "type": "boolean" },
        "requires_block_mask": { "type": "boolean" },
        "requires_expert_router": { "type": "boolean" },
        "metal_device_version": { 
          "type": "string", 
          "enum": ["AppleSilicon_M1", "AppleSilicon_M2", "AppleSilicon_M3", "AppleSilicon_M4"]
        }
      },
      "required": ["min_unified_memory_gb"]
    },
    "functional_flags": {
      "type": "object",
      "description": "Binary features that configure specific runtime optimizations",
      "properties": {
        "supports_streaming": { "type": "boolean" },
        "supports_partial_emit": { "type": "boolean" },
        "supports_expert_prefetch": { "type": "boolean" },
        "supports_async_router": { "type": "boolean" },
        "supports_proxy_attention": { "type": "boolean" }
      }
    }
  },
  "required": ["model_id", "supported_capabilities", "platform_requirements"]
}
```

### Example 1: Nemotron Labs Diffusion
This model requires bidirectional attention, iterative refinement steps, and block masking to reconstruct outputs.

```json
{
  "model_id": "nemotron-labs-diffusion-8b",
  "supported_capabilities": ["diffusion"],
  "platform_requirements": {
    "min_unified_memory_gb": 16,
    "requires_bidirectional_attention": true,
    "requires_block_mask": true,
    "metal_device_version": "AppleSilicon_M2"
  },
  "functional_flags": {
    "supports_streaming": true,
    "supports_partial_emit": true
  }
}
```

### Example 2: Streaming MoE (Mixture of Experts)
This model requires an active routing mechanism to dynamically assign token inputs to specialized hardware blocks.

```json
{
  "model_id": "deepseek-moe-16b",
  "supported_capabilities": ["autoregressive", "streaming_moe"],
  "platform_requirements": {
    "min_unified_memory_gb": 24,
    "requires_expert_router": true,
    "metal_device_version": "AppleSilicon_M3"
  },
  "functional_flags": {
    "supports_expert_prefetch": true,
    "supports_async_router": true,
    "supports_proxy_attention": false
  }
}
```

---

## D1.2: Capability Registry & Descriptors

The **Capability Registry** acts as a metadata service describing all options, default values, validation structures, and dependent rules for each capability.

### Parameter (Option) Schema

Each option within a capability is defined by the following metadata schema:

| Attribute | Type | Description |
| :--- | :--- | :--- |
| `key` | String | Unique programmatic key (e.g. `temperature`). |
| `type` | String | Data type: `boolean`, `integer`, `float`, `string`, `enum`, `model_picker`. |
| `display_name` | String | Localized UI label. |
| `description` | String | User-facing tooltip explaining the parameter. |
| `default` | Any | Out-of-the-box default value when unspecified. |
| `validation` | Object | Bounds (e.g., `min`, `max`, `step`, or `choices` for enums). |
| `visibility` | String | Visual classification: `standard`, `advanced`, `experimental`. |
| `dependencies` | Array | Conditions under which this option is active (e.g., `[ { "option": "dflash_enabled", "value": true } ]`). |

---

## Core Capabilities Definitions

Below are the descriptors for the four canonical capabilities:

### 1. Autoregressive Capability
Controls standard causal token-by-token generation parameters.

```json
{
  "id": "autoregressive",
  "display_name": "Autoregressive Generation",
  "description": "Standard causal generation settings",
  "options": [
    {
      "key": "temperature",
      "type": "float",
      "display_name": "Temperature",
      "description": "Sampling temperature. 0.0 is deterministic.",
      "default": 0.7,
      "validation": { "min": 0.0, "max": 2.0, "step": 0.05 },
      "visibility": "standard"
    },
    {
      "key": "top_p",
      "type": "float",
      "display_name": "Top P",
      "description": "Nucleus sampling threshold.",
      "default": 0.9,
      "validation": { "min": 0.0, "max": 1.0, "step": 0.01 },
      "visibility": "standard"
    },
    {
      "key": "top_k",
      "type": "integer",
      "display_name": "Top K",
      "description": "Limit sampling pool to K candidates.",
      "default": 0,
      "validation": { "min": 0, "max": 500 },
      "visibility": "advanced"
    },
    {
      "key": "min_p",
      "type": "float",
      "display_name": "Min P",
      "description": "Minimum probability floor relative to top token.",
      "default": 0.05,
      "validation": { "min": 0.0, "max": 1.0 },
      "visibility": "advanced"
    },
    {
      "key": "repetition_penalty",
      "type": "float",
      "display_name": "Repetition Penalty",
      "description": "Penalizes repeated tokens. 1.0 = disabled.",
      "default": 1.0,
      "validation": { "min": 0.5, "max": 2.0 },
      "visibility": "standard"
    }
  ]
}
```

### 2. Diffusion Capability
Tunes iterative noise extraction processes.

```json
{
  "id": "diffusion",
  "display_name": "Diffusion Processing",
  "description": "Controls denoising steps and policy",
  "options": [
    {
      "key": "refinement_steps",
      "type": "integer",
      "display_name": "Refinement Steps",
      "description": "Number of denoising steps per cycle.",
      "default": 20,
      "validation": { "min": 1, "max": 100 },
      "visibility": "standard"
    },
    {
      "key": "block_size",
      "type": "integer",
      "display_name": "Block Size",
      "description": "Chunk size for parallel evaluation blocks.",
      "default": 32,
      "validation": { "min": 8, "max": 128, "step": 8 },
      "visibility": "advanced"
    },
    {
      "key": "noise_schedule",
      "type": "enum",
      "display_name": "Noise Schedule",
      "description": "The math policy governing noise reduction rate.",
      "default": "linear",
      "validation": { "choices": ["linear", "cosine", "exponential"] },
      "visibility": "advanced"
    },
    {
      "key": "cfg",
      "type": "float",
      "display_name": "Classifier Free Guidance (CFG)",
      "description": "Strength of alignment with the target prompt.",
      "default": 4.5,
      "validation": { "min": 1.0, "max": 20.0, "step": 0.1 },
      "visibility": "standard"
    },
    {
      "key": "streaming_policy",
      "type": "enum",
      "display_name": "Streaming Policy",
      "description": "How tokens are emitted during refinement cycles.",
      "default": "greedy",
      "validation": { "choices": ["greedy", "conservative", "buffered"] },
      "visibility": "experimental"
    }
  ]
}
```

### 3. Triage (Speculative Decoding) Capability
Configures dual-model acceleration (Draft + Verify) mechanics.

```json
{
  "id": "triage",
  "display_name": "Triage Speculation",
  "description": "Draft-verify spec-decoding knobs",
  "options": [
    {
      "key": "verification_passes",
      "type": "integer",
      "display_name": "Verification Passes",
      "description": "Validation checks executed per batch.",
      "default": 1,
      "validation": { "min": 1, "max": 4 },
      "visibility": "advanced"
    },
    {
      "key": "confidence_threshold",
      "type": "float",
      "display_name": "Confidence Threshold",
      "description": "Minimum token agreement rate to maintain draft block size.",
      "default": 0.85,
      "validation": { "min": 0.5, "max": 1.0, "step": 0.05 },
      "visibility": "standard"
    },
    {
      "key": "draft_model",
      "type": "model_picker",
      "display_name": "Draft Assistant Model",
      "description": "Smaller assistant model sharing the target's tokenizer.",
      "default": null,
      "validation": { "filter": "same_tokenizer" },
      "visibility": "standard"
    },
    {
      "key": "verification_model",
      "type": "model_picker",
      "display_name": "Verification Model",
      "description": "Optional secondary model to perform output verification.",
      "default": null,
      "validation": { "filter": "same_tokenizer" },
      "visibility": "advanced"
    },
    {
      "key": "retry_budget",
      "type": "integer",
      "display_name": "Retry Budget",
      "description": "Permitted evaluation rollbacks when verification fails.",
      "default": 2,
      "validation": { "min": 0, "max": 5 },
      "visibility": "experimental"
    }
  ]
}
```

### 4. Streaming MoE (Mixture of Experts) Capability
Optimizes sparse attention execution, prefetching, and routing thresholds.

```json
{
  "id": "streaming_moe",
  "display_name": "Streaming MoE Routing",
  "description": "Sparse attention and expert budget configuration",
  "options": [
    {
      "key": "routing_policy",
      "type": "enum",
      "display_name": "Routing Policy",
      "description": "Mechanism used to rank and load experts.",
      "default": "top_k",
      "validation": { "choices": ["top_k", "softmax_gated", "hardware_aware"] },
      "visibility": "advanced"
    },
    {
      "key": "streaming_mode",
      "type": "enum",
      "display_name": "Streaming Mode",
      "description": "Prefetch orchestration during computation cycles.",
      "default": "async",
      "validation": { "choices": ["synchronous", "async", "pipelined"] },
      "visibility": "experimental"
    },
    {
      "key": "expert_budget",
      "type": "integer",
      "display_name": "Expert Budget",
      "description": "Cap on concurrent active experts loaded in memory.",
      "default": 4,
      "validation": { "min": 1, "max": 16 },
      "visibility": "standard"
    },
    {
      "key": "memory_budget",
      "type": "string",
      "display_name": "MoE RAM Budget",
      "description": "Cap on absolute unified RAM allocated for expert checkpoints.",
      "default": "16GB",
      "validation": { "pattern": "^[0-9]+[MGB]B$" },
      "visibility": "advanced"
    }
  ]
}
```
