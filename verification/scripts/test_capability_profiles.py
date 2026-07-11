# SPDX-License-Identifier: Apache-2.0
"""Test capability profiles for different engine classes."""

import json
import pytest
import numpy as np

class MockEngine:
    def __init__(self, family):
        self.family = family

    def generate(self, prompt, seed=42):
        if self.family == "diffusion":
            rng = np.random.default_rng(seed)
            return rng.normal(0, 1, (64, 64))
        elif self.family == "dense_ar":
            return [1, 5, 23, 44]
        raise ValueError("Unsupported family")

@pytest.fixture
def load_seeds():
    # Load fallback values if the JSON seed file is not present
    try:
        with open("verification/seeds/diffusion.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "profiles": {
                "standard_portrait": {"seed": 1024}
            }
        }

@pytest.mark.parametrize("engine_family", ["dense_ar", "diffusion"])
def test_engine_capability_profiles(engine_family, load_seeds):
    engine = MockEngine(engine_family)
    
    if engine_family == "diffusion":
        seed = load_seeds["profiles"]["standard_portrait"]["seed"]
        output = engine.generate("portrait of a scientist", seed=seed)
        
        expected_shape = (64, 64)
        assert output.shape == expected_shape, "Diffusion output shape mismatch."
        assert np.isfinite(output).all(), "Diffusion outputs contain NaN/Inf."
        
    elif engine_family == "dense_ar":
        output = engine.generate("Why is the sky blue?")
        assert len(output) > 0, "No tokens returned from Autoregressive engine."
        assert all(isinstance(t, int) for t in output), "Tokens must be integers."

def test_engine_failure_mode_reproduce():
    """Verify that unsupported parameters raise expected failure modes."""
    with pytest.raises(ValueError, match="Unsupported family"):
        MockEngine("unknown_family").generate("test")
