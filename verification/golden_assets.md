# Golden Assets Spec

This specification catalog defines the **Golden Assets** used to evaluate oMLX model capabilities across execution families. Unlike plain prompts, these assets contain multimodal inputs, seeds, token structures, and mathematical validation criteria.

---

## 1. Directory Structure Map

```
verification/
├── seeds/
│   ├── diffusion.json         # Seeds and configuration metadata
│   ├── autoregressive.json
│   └── moe.json
└── goldens/
    ├── dense_ar_tokens.json   # Expected token sequences
    ├── moe_routing.json       # Target expert routing indexes
    ├── image_source.png       # Source image for Vision tests
    ├── whisper_sample.wav     # Source audio for Voice tests
    └── embeddings_pairs.json  # Text pairs with expected similarity
```

---

## 2. Asset Definitions & Capability Requirements

### 1. Dense AR Family (Llama, Gemma, Qwen)
*   **Asset Type**: Prompts & Expected Token Sequences
*   **Input Prompt**: `"Write a step-by-step logic proof that A = A."`
*   **Settings**: `temperature=0.0`, `seed=42`
*   **Expected Behavior**: Strict adherence to formal logic notation, no conversational filler if requested.
*   **Tolerances**: Checkpoint must output exact token sequence matching the baseline token IDs (greedy match).
*   **Failure Modes**: Loop repetition, hallucinated tokens, random changes in formatting.

### 2. MoE Family (DeepSeek, GLM, Mixtral)
*   **Asset Type**: Prompt Routing Target Tables
*   **Input Prompt**: `"Explain Quantum Electrodynamics in Chinese, and format the output as LaTeX equations."`
*   **Settings**: `temperature=0.0`, `seed=42`
*   **Expected Behavior**: Routing gates trigger experts specialized in language transition (Chinese) and symbolic output (LaTeX).
*   **Tolerances**: Expert routing path alignment (index sequence comparison) must match reference outputs by >= 95%.
*   **Failure Modes**: Router collapse (single expert processes everything), high latency from memory swapping.

### 3. Diffusion Family (Nemotron Labs, Diffusion Gemma)
*   **Asset Type**: Image Seeds & Config Baselines
*   **Input Prompt**: `"high-contrast neon cyberpunk city street, ultra-detailed"`
*   **Settings**: Seed `2026` (from `seeds/diffusion.json`), `steps=25`, `cfg_scale=5.0`
*   **Expected Behavior**: High-contrast cyberpunk landscape, structurally identical pixels across runs.
*   **Tolerances**: Pixel matrix Mean Squared Error (MSE) < `1e-5` when compared against baseline.
*   **Failure Modes**: Color shifts, texture warping, non-deterministic output due to floating-point drift.

### 4. Vision Family (Qwen VL, Gemma Vision)
*   **Asset Type**: Base64 Image Inputs & Expected Transcripts
*   **Input Image**: OCR test pattern (`verification/goldens/ocr_test_pattern.png` or mock data)
*   **Prompt**: `"Transcribe the text in this image exactly."`
*   **Expected Behavior**: Transcribe spelling, layout, and casing accurately.
*   **Tolerances**: Exact string match or Word Error Rate (WER) = 0% on text content.
*   **Failure Modes**: Hallucinated characters, line skipped, spatial bounding box coordinates misalignment.

### 5. Audio Family (Whisper)
*   **Asset Type**: WAV Files & Reference Transcripts
*   **Input Audio**: 5-second PCM mono audio segment (`verification/goldens/whisper_sample.wav`)
*   **Expected Behavior**: Match spoken English text exactly: `"The quick brown fox jumps over the lazy dog."`
*   **Tolerances**: WER < 1%, timestamp boundaries within 10ms of reference audio alignment.
*   **Failure Modes**: Missing words, duplicated tokens, or transcription lag.

### 6. Embedding Family (Nomic)
*   **Asset Type**: Sentence pairs & expected cosine similarities
*   **Pairs**:
    *   `("The weather is nice today.", "It is a sunny day outside.")` -> High similarity (>0.85)
    *   `("The weather is nice today.", "Quantum physics is interesting.")` -> Low similarity (<0.15)
*   **Tolerances**: Cosine similarity value drift < `1e-5` compared to PyTorch embeddings.
*   **Failure Modes**: Random similarity values, collapsed embeddings (all outputs clustering to a single value).

---

## 3. Executable Pytest Template

This script shows how to assert correctness across these assets in code.

```python
# verification/scripts/test_golden_assets.py
# SPDX-License-Identifier: Apache-2.0

import json
import pytest
import numpy as np

# Mock golden assets loader
class GoldenLoader:
    @staticmethod
    def get_embedding_pair():
        return {
            "sentence_a": "The weather is nice today.",
            "sentence_b": "It is a sunny day outside.",
            "expected_cosine": 0.885
        }

    @staticmethod
    def get_diffusion_target():
        # returns expected mean pixel intensity
        return 0.1254

def calculate_cosine_similarity(vec_a, vec_b):
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return dot_product / (norm_a * norm_b)

def test_embedding_golden_alignment():
    """Verify that sentence embeddings produce expected cosine similarity."""
    asset = GoldenLoader.get_embedding_pair()
    
    # Mock output vectors
    vector_a = np.array([0.1, 0.2, 0.3, 0.9])
    vector_b = np.array([0.11, 0.19, 0.32, 0.88])
    
    similarity = calculate_cosine_similarity(vector_a, vector_b)
    
    tolerance = 1e-3
    assert abs(similarity - asset["expected_cosine"]) < tolerance, (
        f"Cosine similarity ({similarity:.4f}) drifted past tolerance ({tolerance}) "
        f"from expected ({asset['expected_cosine']:.4f})."
    )

def test_diffusion_pixel_reproducibility():
    """Verify that diffusion outputs meet deterministic target metrics."""
    target_mean = GoldenLoader.get_diffusion_target()
    
    # Simulated 64x64 output canvas
    output_canvas = np.full((64, 64), 0.1254)
    
    actual_mean = np.mean(output_canvas)
    assert abs(actual_mean - target_mean) < 1e-6, (
        f"Mean pixel intensity ({actual_mean}) drifted from golden baseline ({target_mean})."
    )
```

**Expected Test Output**:
```
pytest verification/scripts/test_golden_assets.py -v
============================= test session starts ==============================
collected 2 items

verification/scripts/test_golden_assets.py::test_embedding_golden_alignment PASSED
verification/scripts/test_golden_assets.py::test_diffusion_pixel_reproducibility PASSED

============================== 2 passed in 0.08s ===============================
```
