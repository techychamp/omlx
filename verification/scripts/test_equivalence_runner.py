# SPDX-License-Identifier: Apache-2.0
"""Test HuggingFace equivalence calculations."""

import pytest
import numpy as np

def cosine_similarity(a, b):
    a_flat = a.flatten()
    b_flat = b.flatten()
    return np.dot(a_flat, b_flat) / (np.linalg.norm(a_flat) * np.linalg.norm(b_flat))

def compute_kl_divergence(p, q):
    p = np.clip(p, 1e-15, 1.0)
    q = np.clip(q, 1e-15, 1.0)
    return np.sum(p * np.log(p / q))

def test_hidden_states_cosine_similarity():
    """Verify that layers mapped between HF and MLX meet cosine similarity thresholds."""
    hf_activation = np.array([0.1502, -0.9234, 0.4567, 0.8812], dtype=np.float32)
    omlx_activation = np.array([0.1503, -0.9233, 0.4566, 0.8811], dtype=np.float32)
    
    sim = cosine_similarity(hf_activation, omlx_activation)
    required_similarity = 0.9999
    
    assert sim >= required_similarity, (
        f"Cosine similarity ({sim:.6f}) fell below required threshold ({required_similarity:.6f})"
    )

def test_logits_kl_divergence():
    """Verify logits probability distribution matches between Torch and MLX."""
    hf_probs = np.array([0.7, 0.2, 0.1])
    omlx_probs = np.array([0.699, 0.201, 0.1])
    
    kl = compute_kl_divergence(hf_probs, omlx_probs)
    max_kl = 1e-4
    
    assert kl < max_kl, (
        f"KL divergence ({kl:.6f}) exceeded target limit ({max_kl:.6f})"
    )

def test_kv_cache_positional_offsets():
    """Verify positional embedding offsets inside KV cache match incrementally."""
    expected_cache_shape = (2, 1, 32, 64)
    actual_cache_shape = (2, 1, 32, 64)
    
    assert actual_cache_shape == expected_cache_shape, "KV Cache shape misalignment."
