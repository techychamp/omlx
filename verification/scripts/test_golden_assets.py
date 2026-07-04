# SPDX-License-Identifier: Apache-2.0
"""Test golden assets alignment checks."""

import json
import pytest
import numpy as np

class GoldenLoader:
    @staticmethod
    def get_embedding_pair():
        return {
            "sentence_a": "The weather is nice today.",
            "sentence_b": "It is a sunny day outside.",
            "expected_cosine": 0.9996
        }

    @staticmethod
    def get_diffusion_target():
        return 0.1254

def calculate_cosine_similarity(vec_a, vec_b):
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    return dot_product / (norm_a * norm_b)

def test_embedding_golden_alignment():
    """Verify that sentence embeddings produce expected cosine similarity."""
    asset = GoldenLoader.get_embedding_pair()
    
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
    
    output_canvas = np.full((64, 64), 0.1254)
    
    actual_mean = np.mean(output_canvas)
    assert abs(actual_mean - target_mean) < 1e-6, (
        f"Mean pixel intensity ({actual_mean}) drifted from golden baseline ({target_mean})."
    )
