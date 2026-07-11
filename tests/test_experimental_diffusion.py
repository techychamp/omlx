# SPDX-License-Identifier: Apache-2.0
"""
Tests for Experimental Nemotron Diffusion backend.
"""

import pytest
import mlx.core as mx

from omlx.inference.execution_profile import ExecutionProfile, ExecutionContext, get_profile_registry
from omlx.registry.model_info import ModelInfo
from omlx.runtime.capabilities import EngineCapabilities, FeatureFlags, ModelCapabilities
from omlx.inference.backends.experimental_diffusion_backend import ExperimentalNemotronBackend, NemotronDiffusionPipeline, NemotronExecutionEngine
from omlx.models.adapters.nemotron_adapter import NemotronModelAdapter
from omlx.inference.strategy_types import ForwardResult

class MockModel:
    def __init__(self):
        class Config:
            mask_token_id = 100
            model_type = "nemotron_labs_diffusion"
            architectures = ["NemotronLabsDiffusionModel"]
        self.config = Config()
        
    def __call__(self, inputs, mask=None, **kwargs):
        batch, seq_len = inputs.shape
        # return dummy logits: [batch, seq_len, vocab_size]
        return mx.zeros((batch, seq_len, 200))

def test_nemotron_mask_generation():
    adapter = NemotronModelAdapter(MockModel(), block_size=32)
    adapter.enable_diffusion_mode()
    
    # 10 prefix tokens, 32 diffusion tokens -> q_len = 42
    mask = adapter.create_diffusion_mask(q_len=42, prefix_len=10)
    
    assert mask.shape == (42, 42)
    # The mask should be float32 with 0.0 and -inf
    assert mask.dtype == mx.float32

def test_backend_resolution():
    registry = get_profile_registry()
    model_info = ModelInfo(
        model_path="dummy",
        architecture="NemotronLabsDiffusionModel",
        config_model_type="nemotron_labs_diffusion",
        capabilities=ModelCapabilities(supports_diffusion=True),
        generation_modes=[],
        preferred_generation_mode="diffusion",
        cache_type="kv",
        attention_modes=[],
        supports_streaming=True,
        tokenizer_info={}
    )
    context = ExecutionContext(
        model_info=model_info,
        engine_capabilities=EngineCapabilities(supports_diffusion=True),
        feature_flags=FeatureFlags(DIFFUSION_ENABLED=True)
    )
    
    profile, factory = registry.resolve(context)
    assert profile.backend_name == "experimental_nemotron"
    
    backend = factory(profile, context)
    assert isinstance(backend, ExperimentalNemotronBackend)
    assert isinstance(backend.pipeline, NemotronDiffusionPipeline)

def test_pipeline_execution():
    model = MockModel()
    adapter = NemotronModelAdapter(model, block_size=32)
    engine = NemotronExecutionEngine(adapter)
    backend = ExperimentalNemotronBackend(engine)
    
    inputs = {"prefix": mx.array([[1, 2, 3]])}
    result = backend.execute_cycle(inputs)
    
    assert isinstance(result, ForwardResult)
    assert "final_tokens" in result.extra
    assert result.extra["final_tokens"].shape == (1, 32)
