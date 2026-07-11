# Verification Framework Spec

This specification describes the **Scientific Verification Framework** for oMLX checkpoints. It governs the validation pipeline to confirm that runtime modifications or structural alterations do not break correctness, alignment, or execution capabilities.

---

## 1. Philosophy & Testing Layers

### Foundational Principles
*   **Hermeticity**: Tests run against pinned, reproducible configurations and deterministic seeds.
*   **Scientific Derivation**: Expected outputs, tolerances, and configurations must be derived directly from official reference implementations (e.g., Hugging Face transformers, official papers) or known-good baselines. No magic numbers allowed.
*   **Verification Leveling**: Metrics are tied to a structured maturity model.

### Verification Maturity Model
```
[Level 0: No Verification]
         │
         ▼
[Level 1: Unit Tests] (Verifies basic modules and API routes in isolation)
         │
         ▼
[Level 2: Golden Tests] (Executes deterministic test assets against local engines)
         │
         ▼
[Level 3: HF Equivalence] (Proves tensor-level alignment with PyTorch references)
         │
         ▼
[Level 4: Performance Baseline] (Validates throughput, latencies, and resource ceilings)
         │
         ▼
[Level 5: Regression Protected] (CI blocks merges on any detected degradations)
```

---

## 2. Architecture & Directory Layout

The verification subsystem is isolated under `/verification/`:

```
verification/
├── verification_framework.md   # [THIS FILE] Core design & maturity spec
├── golden_assets.md            # Asset catalog across model modalities
├── hf_equivalence.md           # PyTorch vs MLX layer mapping & equivalence harness
├── performance_framework.md    # Metrics tracking (TTFT, TPS, Peak RAM)
├── verification_execution.md   # Execution flow stages
├── confidence_model.md         # Weighted confidence score model
├── automation.md               # CI/CD integration rules & PR gateways
├── seeds/                      # Seed database files for deterministic runs
├── schema/                     # JSON validation schemas for reports
├── goldens/                    # Stored inputs and targets by version
│   ├── v1/
│   ├── v2/
│   └── nightly/
├── baselines/                  # Pinned metrics and accuracy logs
│   ├── v1/
│   ├── v2/
│   └── nightly/
├── reports/                    # Generated checkpoint reports
└── scripts/                    # Test harnesses and report builders
```

---

## 3. Execution Capability Verification Profiles

Models are grouped into **Execution Families** and evaluated against specialized verification profiles.

| Capability Profile | Target Execution Family | Primary Metrics | Key Verification Targets | Expected Tolerances |
| :--- | :--- | :--- | :--- | :--- |
| **Dense AR Profile** | `dense_ar` (Llama, Gemma, Qwen) | TTFT, TPS, Token IDs, Logits | Greedy text generation, System prompt obedience | Logit L2 difference < `1e-4`, exact match on top token |
| **MoE Profile** | `moe` (DeepSeek, GLM, Mixtral) | Routing ratios, Load variance, TPS | Token distribution, dynamic experts activation | Routing choice exact match, expert activation load skew < 5% |
| **Diffusion Profile** | `diffusion` (Nemotron Labs, Diffusion Gemma) | Structural Similarity (SSIM), MSE | Noise scheduler correctness, deterministic seed images | Image SSIM > `0.99` against PyTorch reference seed |
| **Vision Profile** | `vision` (Qwen VL, Gemma Vision) | Token alignment, image projection outputs | Multi-modal projection alignments, OCR extraction accuracy | Exact text match on target OCR golden assets |
| **Audio Profile** | `audio` (Whisper) | Word Error Rate (WER), token latencies | Transcription equivalence, timestamp matching | WER < 1% on reference audio clips, timestamp drift < 10ms |
| **Embedding Profile** | `embedding` (Nomic, etc.) | Cosine similarity, L2 distance | Semantic mapping, retrieval ranking | Embedding vector Cosine Similarity > `0.9999` |

---

## 4. Execution Capabilities Matrix

### Autoregressive (AR)
*   **Verification Strategy**: Validate deterministic sequence decoding. Ensure repetition penalties, temperature boundaries, and system prompts are obeyed.
*   **Failure Modes**: Degraded token diversity, repetition loops, or ignoring system directives.
*   **Tolerances**: Logit output array must align exactly with the reference target under greedy decoding (temperature=0.0).

### Diffusion
*   **Verification Strategy**: Leverage structural image similarity (SSIM) or mean squared error (MSE) on output pixel tensors generated under pinned seeds (from `seeds/diffusion.json`).
*   **Failure Modes**: Image degradation, high variance due to unpinned random generator seeds, or corrupted noise schedules.
*   **Tolerances**: Pixel output MSE < `1e-5` when comparing MLX/oMLX canvas generation with raw MLX reference arrays.

### Triage / Capability Router
*   **Verification Strategy**: Verify scheduler routing logic when receiving request payloads requiring dynamic triage (e.g. prompt classification, routing to specialized engines).
*   **Failure Modes**: Request routed to invalid engine pool, failed fallback transitions.
*   **Tolerances**: 100% classification matching against pre-labeled triage golden arrays.

### Streaming MoE (Mixture of Experts)
*   **Verification Strategy**: Inspect the activation maps of gating networks across layers. Ensure the correct top-k experts are chosen per token step during active decode.
*   **Failure Modes**: Expert collapse (routing all tokens to the same expert), incorrect scaling weights, or out-of-order expert loading.
*   **Tolerances**: Zero divergence in routing decisions compared to reference framework output for a given prompt input.

---

## 5. Executable Pytest Template

This template shows how a capability profile maps to a pytest fixture execution.

```python
# verification/scripts/test_capability_profiles.py
# SPDX-License-Identifier: Apache-2.0

import json
import pytest
import numpy as np

# Mock execution backend representable of oMLX models
class MockEngine:
    def __init__(self, family):
        self.family = family

    def generate(self, prompt, seed=42):
        if self.family == "diffusion":
            # Simulate image matrix output
            rng = np.random.default_rng(seed)
            return rng.normal(0, 1, (64, 64))
        elif self.family == "dense_ar":
            return [1, 5, 23, 44] # Mock Token IDs
        raise ValueError("Unsupported family")

@pytest.fixture
def load_seeds():
    with open("verification/seeds/diffusion.json") as f:
        return json.load(f)

@pytest.mark.parametrize("engine_family", ["dense_ar", "diffusion"])
def test_engine_capability_profiles(engine_family, load_seeds):
    engine = MockEngine(engine_family)
    
    if engine_family == "diffusion":
        seed = load_seeds["profiles"]["standard_portrait"]["seed"]
        output = engine.generate("portrait of a scientist", seed=seed)
        
        # Golden reference check (simulated target value)
        expected_shape = (64, 64)
        assert output.shape == expected_shape, "Diffusion output shape mismatch."
        assert np.isfinite(output).all(), "Diffusion outputs contain NaN/Inf."
        
    elif engine_family == "dense_ar":
        output = engine.generate("Why is the sky blue?")
        assert len(output) > 0, "No tokens returned from Autoregressive engine."
        assert all(isinstance(t, int) for t in output), "Tokens must be integers."

def test_engine_failure_mode_reproduce():
    """Verify that unsupported parameters raise expected failure modes."""
    engine = MockEngine("dense_ar")
    with pytest.raises(ValueError, match="Unsupported family"):
        MockEngine("unknown_family").generate("test")
```

**Expected Test Output**:
```
pytest verification/scripts/test_capability_profiles.py -v
============================= test session starts ==============================
collected 3 items

verification/scripts/test_capability_profiles.py::test_engine_capability_profiles[dense_ar] PASSED
verification/scripts/test_capability_profiles.py::test_engine_capability_profiles[diffusion] PASSED
verification/scripts/test_capability_profiles.py::test_engine_failure_mode_reproduce PASSED

============================== 3 passed in 0.12s ===============================
```
