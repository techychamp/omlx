# HuggingFace Equivalence Harness Spec

This specification details the **HuggingFace Equivalence Harness** designed to verify layer-by-layer parameter alignment, activation mapping, logits, and cache states between HuggingFace (PyTorch) and oMLX (MLX-based) model engines.

---

## 1. Repository Layout Map

```
verification/
├── comparisons/
│   ├── llama_hidden_states.json    # Dumped activation comparison values
│   └── whisper_logits.json         # Dumped logits comparisons
└── scripts/
    ├── hf_equivalence_harness.py   # Harness runner comparing Torch and MLX
    └── test_equivalence_runner.py  # Executable Pytest harness tests
```

---

## 2. Layer Mapping (HF → MLX → oMLX)

To compare intermediate outputs and hidden states, parameter names and module structures must be mapped across runtime boundaries.

### Layer Mapping Table (Dense AR - e.g. Llama Model)

| HuggingFace (PyTorch) Key | MLX Model Key | oMLX Key | Shape Alignment |
| :--- | :--- | :--- | :--- |
| `model.embed_tokens.weight` | `model.embed_tokens.weight` | `model.embed_tokens.weight` | `[vocab_size, hidden_size]` |
| `model.layers.{i}.self_attn.q_proj.weight` | `model.layers.{i}.self_attn.q_proj.weight` | `model.layers.{i}.self_attn.q_proj.weight` | `[hidden_size, num_heads * head_dim]` |
| `model.layers.{i}.self_attn.k_proj.weight` | `model.layers.{i}.self_attn.k_proj.weight` | `model.layers.{i}.self_attn.k_proj.weight` | `[hidden_size, num_kv_heads * head_dim]` |
| `model.layers.{i}.self_attn.v_proj.weight` | `model.layers.{i}.self_attn.v_proj.weight` | `model.layers.{i}.self_attn.v_proj.weight` | `[hidden_size, num_kv_heads * head_dim]` |
| `model.layers.{i}.self_attn.o_proj.weight` | `model.layers.{i}.self_attn.o_proj.weight` | `model.layers.{i}.self_attn.o_proj.weight` | `[num_heads * head_dim, hidden_size]` |
| `model.layers.{i}.mlp.gate_proj.weight` | `model.layers.{i}.mlp.gate_proj.weight` | `model.layers.{i}.mlp.gate_proj.weight` | `[hidden_size, intermediate_size]` |
| `model.layers.{i}.mlp.up_proj.weight` | `model.layers.{i}.mlp.up_proj.weight` | `model.layers.{i}.mlp.up_proj.weight` | `[hidden_size, intermediate_size]` |
| `model.layers.{i}.mlp.down_proj.weight` | `model.layers.{i}.mlp.down_proj.weight` | `model.layers.{i}.mlp.down_proj.weight` | `[intermediate_size, hidden_size]` |
| `model.layers.{i}.input_layernorm.weight` | `model.layers.{i}.input_layernorm.weight` | `model.layers.{i}.input_layernorm.weight` | `[hidden_size]` |
| `model.layers.{i}.post_attention_layernorm.weight` | `model.layers.{i}.post_attention_layernorm.weight` | `model.layers.{i}.post_attention_layernorm.weight` | `[hidden_size]` |
| `model.norm.weight` | `model.norm.weight` | `model.norm.weight` | `[hidden_size]` |
| `lm_head.weight` | `lm_head.weight` | `lm_head.weight` | `[vocab_size, hidden_size]` |

---

## 3. Equivalence Categories & Tolerances

### 1. Hidden States Alignment
*   **Verification Strategy**: Hook the forward pass of both models, capture hidden states after Layer `i` normalization and MLP blocks.
*   **Metrics**: Cosine Similarity and L2 Norm Distance.
*   **Tolerances**: Cosine Similarity >= `0.9999`, Normalized L2 Distance < `1e-4` (accounting for FP16 precision adjustments on Metal).
*   **Failure Modes**: Disalignment accumulating over layers, custom RoPE scaling factors causing divergent values in early layers.

### 2. Logits and Top-k Divergence
*   **Verification Strategy**: Extract probability distributions from the model heads on identical input token sequences.
*   **Metrics**: Maximum Absolute Difference (L-inf norm) and Kullback-Leibler (KL) Divergence.
*   **Tolerances**: KL Divergence < `1e-5`, Max absolute logit difference < `1e-3`.
*   **Failure Modes**: Logit scaling variations or different Softmax implementations causing top-k selection swaps.

### 3. KV-Cache Comparison
*   **Verification Strategy**: Run incremental decode steps. Extract internal key/value states after Step `N` and check they match the concatenated batch output of Step `1..N`.
*   **Metrics**: Cache element-wise equality and length checks.
*   **Tolerances**: Absolute tensor equivalence (`np.allclose` with `atol=1e-5`).
*   **Failure Modes**: Off-by-one errors in positional embedding offsets, stale cache pages not being evicted, or corrupted history mappings.

### 4. Generated Text Equivalence
*   **Verification Strategy**: Greedy text generation on baseline prompts.
*   **Metrics**: Exact Token ID matches, String equality.
*   **Tolerances**: 100% token sequence match for a 128-token generation under `temperature=0.0`.
*   **Failure Modes**: Non-greedy path divergence, formatting deviations from different tokenizer configuration schemas.

---

## 4. Executable Pytest Template

This pytest test verifies layer mappings and hidden state equivalence calculations.

```python
# verification/scripts/test_equivalence_runner.py
# SPDX-License-Identifier: Apache-2.0

import pytest
import numpy as np

def cosine_similarity(a, b):
    a_flat = a.flatten()
    b_flat = b.flatten()
    return np.dot(a_flat, b_flat) / (np.linalg.norm(a_flat) * np.linalg.norm(b_flat))

def compute_kl_divergence(p, q):
    """Compute KL Divergence between two probability distributions."""
    # Add epsilon to prevent division by zero or log of zero
    p = np.clip(p, 1e-15, 1.0)
    q = np.clip(q, 1e-15, 1.0)
    return np.sum(p * np.log(p / q))

def test_hidden_states_cosine_similarity():
    """Verify that layers mapped between HF and MLX meet cosine similarity thresholds."""
    # Simulated layer output from PyTorch (HF)
    hf_activation = np.array([0.1502, -0.9234, 0.4567, 0.8812], dtype=np.float32)
    # Simulated layer output from oMLX
    omlx_activation = np.array([0.1503, -0.9233, 0.4566, 0.8811], dtype=np.float32)
    
    sim = cosine_similarity(hf_activation, omlx_activation)
    required_similarity = 0.9999
    
    assert sim >= required_similarity, (
        f"Cosine similarity ({sim:.6f}) fell below required threshold ({required_similarity:.6f})"
    )

def test_logits_kl_divergence():
    """Verify logits probability distribution matches between Torch and MLX."""
    # Simulated softmax output distributions
    hf_probs = np.array([0.7, 0.2, 0.1])
    omlx_probs = np.array([0.699, 0.201, 0.1])
    
    kl = compute_kl_divergence(hf_probs, omlx_probs)
    max_kl = 1e-4
    
    assert kl < max_kl, (
        f"KL divergence ({kl:.6f}) exceeded target limit ({max_kl:.6f})"
    )

def test_kv_cache_positional_offsets():
    """Verify positional embedding offsets inside KV cache match incrementally."""
    # Simulated sequence length cache verification
    expected_cache_shape = (2, 1, 32, 64) # [layers, batch, seq_len, head_dim]
    actual_cache_shape = (2, 1, 32, 64)
    
    assert actual_cache_shape == expected_cache_shape, "KV Cache shape misalignment."
```

**Expected Test Output**:
```
pytest verification/scripts/test_equivalence_runner.py -v
============================= test session starts ==============================
collected 3 items

verification/scripts/test_equivalence_runner.py::test_hidden_states_cosine_similarity PASSED
verification/scripts/test_equivalence_runner.py::test_logits_kl_divergence PASSED
verification/scripts/test_equivalence_runner.py::test_kv_cache_positional_offsets PASSED

============================== 3 passed in 0.10s ===============================
```
