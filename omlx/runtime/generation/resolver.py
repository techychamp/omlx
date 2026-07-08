# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional
from pathlib import Path
from types import MappingProxyType

from omlx.framework.model_intelligence.registry import ModelRegistry
from omlx.runtime.generation.strategy import GenerationStrategy
from omlx.runtime.generation.standard import StandardGenerationStrategy
from omlx.runtime.generation.speculative import SpeculativeGenerationStrategy
from omlx.runtime.generation.diffusion import DiffusionGenerationStrategy

class StrategyResolver:
    """
    Resolves the appropriate generation strategy (Standard, Speculative, Diffusion)
    based on Model Intelligence and capabilities.
    """

    def __init__(self, registry: ModelRegistry):
        self._registry = registry

    def resolve_strategy(self, model_id: str, **kwargs) -> GenerationStrategy:
        descriptor = self._registry.get(model_id)
        
        # If not found in registry, we can run model discovery/intelligence scan
        # on the path if it exists, or create a default descriptor
        if not descriptor:
            model_path = Path(model_id)
            if model_path.exists():
                from omlx.framework.model_intelligence.discovery import ModelDiscoveryFramework
                try:
                    descriptor = ModelDiscoveryFramework().inspect(model_path, model_id)
                except Exception:
                    pass
                    
        # Fallback default descriptor if still not found
        if not descriptor:
            from omlx.framework.model_intelligence.descriptor import ModelDescriptor
            # Construct a default autoregressive model descriptor
            descriptor = ModelDescriptor(
                model_id=model_id,
                model_family="Autoregressive",
                architecture="Transformer",
                architecture_family="Transformer",
                architecture_generation="Unknown",
                task="Text-Generation",
                modality="Text",
                parameter_count=0,
                hidden_size=2048,
                layer_count=22,
                context_length=2048,
                attention_type="Standard",
                activation_type="unknown",
                tokenizer_family="Unknown",
                special_token_information=MappingProxyType({}),
                moe_information=MappingProxyType({}),
                expert_count=0,
                expert_size=0,
                kv_cache_support=True,
                speculative_support=(kwargs.get("strategy") == "speculative"),
                streaming_support=True,
                expert_support=False,
                vision_support=False,
                audio_support=False,
                tool_support=False,
                embedding_support=False,
                reranking_support=False,
                quantization_support=False,
                backend_requirements=("mlx",),
                license="Unknown",
                repository_metadata=MappingProxyType({}),
                recommended_backend="mlx",
                recommended_quantization="none",
                recommended_execution_mode="batched",
                recommended_scheduler="continuous",
                compatibility_report=MappingProxyType({}),
                validation_report=MappingProxyType({}),
                planner_metadata=MappingProxyType({}),
                compiler_metadata=MappingProxyType({})
            )

        # 1. Diffusion check
        is_diffusion = False
        if getattr(descriptor, "model_family", "").lower() == "diffusion":
            is_diffusion = True
        elif getattr(descriptor, "task", "").lower() == "image-generation":
            is_diffusion = True
            
        if is_diffusion:
            plan = kwargs.get("diffusion_plan") or kwargs.get("plan")
            if not plan:
                from omlx.planner.domains.diffusion import DiffusionPlan
                plan = DiffusionPlan(timestep_schedule=[1000, 800, 600, 400, 200, 0])
            return DiffusionGenerationStrategy(plan=plan)

        # 2. Speculative check
        is_speculative = False
        if getattr(descriptor, "speculative_support", False):
            is_speculative = True
        elif kwargs.get("strategy") == "speculative":
            is_speculative = True
            
        if is_speculative:
            return SpeculativeGenerationStrategy()

        # 3. Default standard autoregressive
        return StandardGenerationStrategy()
