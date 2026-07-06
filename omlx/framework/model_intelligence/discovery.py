# SPDX-License-Identifier: Apache-2.0
"""
ModelDiscoveryFramework implementation.

Responsible for inspecting model metadata, configuration, architecture, and tokenizer
without loading weights.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from types import MappingProxyType
import json
import logging
import concurrent.futures

from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.framework.model_intelligence.classifier import ModelClassifier
from omlx.framework.model_intelligence.extractor import CapabilityExtractor
from omlx.framework.model_intelligence.normalizer import MetadataNormalizer

logger = logging.getLogger(__name__)

class ModelDiscoveryFramework:
    _cache: Dict[str, ModelDescriptor] = {}

    def __init__(self):
        self.classifier = ModelClassifier()
        self.extractor = CapabilityExtractor()
        self.normalizer = MetadataNormalizer()

    def _read_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read {path}: {e}")
            return {}

    def _read_text(self, path: Path) -> str:
        if not path.exists():
            return ""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Failed to read {path}: {e}")
            return ""

    def inspect_parallel(self, model_dirs: list[Path], model_ids: list[str]) -> list[ModelDescriptor]:
        """Inspects multiple model directories in parallel."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.inspect, md, mid) for md, mid in zip(model_dirs, model_ids)]
            return [f.result() for f in futures]

    def inspect(self, model_dir: Path, model_id: str) -> ModelDescriptor:
        """
        Inspects a model directory and returns a unified ModelDescriptor.
        Does not load model weights.
        """
        model_dir = Path(model_dir)
        cache_key = f"{model_id}:{model_dir}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Read Raw Metadata
        raw_config = self._read_json(model_dir / "config.json")
        generation_config = self._read_json(model_dir / "generation_config.json")
        tokenizer_config = self._read_json(model_dir / "tokenizer_config.json")
        tokenizer_json = self._read_json(model_dir / "tokenizer.json")
        special_tokens_map = self._read_json(model_dir / "special_tokens_map.json")
        readme = self._read_text(model_dir / "README.md")

        # Safetensors metadata reading would go here (reading just headers)
        # We simulate it for now as returning empty dict unless we implement a struct unpacker.
        safetensors_metadata = {}

        raw_metadata = {
            "config": raw_config,
            "generation": generation_config,
            "tokenizer": tokenizer_config,
            "tokenizer_json": tokenizer_json,
            "special_tokens_map": special_tokens_map,
            "readme": readme,
            "safetensors_metadata": safetensors_metadata,
            "model_id": model_id,
            "path": str(model_dir)
        }

        # 2. Normalize Metadata
        normalized = self.normalizer.normalize(raw_metadata)

        # 3. Classify Architecture & Family
        family, arch, task, modality = self.classifier.classify(normalized)

        # Extended classification
        architecture_family = self.classifier.classify_architecture_family(arch)
        architecture_generation = self.classifier.classify_architecture_generation(arch, normalized)
        tokenizer_family = self.classifier.classify_tokenizer_family(tokenizer_config, tokenizer_json)

        # 4. Extract Capabilities
        caps = self.extractor.extract(normalized, arch, family)

        # 5. Extract structural stats
        param_count = normalized.get("num_parameters", 0)  # Often missing without loading weights
        hidden_size = normalized.get("hidden_size", 0)
        layer_count = normalized.get("num_hidden_layers", 0)
        context_length = normalized.get("context_length", 2048)

        # MoE Info
        moe_info = {}
        expert_count = 0
        expert_size = 0
        if family == "Mixture of Experts":
            expert_count = normalized.get("num_local_experts", normalized.get("num_experts", 0))
            if expert_count > 0 and hidden_size > 0:
                expert_size = hidden_size * 4 # rough estimate
            moe_info = {"num_experts": expert_count, "expert_size": expert_size}

        # License
        license_str = "Unknown"
        if "license" in raw_config:
            license_str = raw_config["license"]
        elif "license" in readme.lower():
            license_str = "See README" # Fallback heuristic

        # 6. Build Descriptor
        descriptor = ModelDescriptor(
            model_id=model_id,
            model_family=family,
            architecture=arch,
            architecture_family=architecture_family,
            architecture_generation=architecture_generation,
            task=task,
            modality=modality,
            parameter_count=param_count,
            hidden_size=hidden_size,
            layer_count=layer_count,
            context_length=context_length,
            attention_type=caps.get("attention_type", "Standard"),
            activation_type=normalized.get("hidden_act", "unknown"),
            tokenizer_family=tokenizer_family,
            special_token_information=MappingProxyType(special_tokens_map),
            moe_information=MappingProxyType(moe_info),
            expert_count=expert_count,
            expert_size=expert_size,
            kv_cache_support=caps.get("kv_cache_support", False),
            speculative_support=caps.get("speculative_support", False),
            streaming_support=caps.get("streaming_support", False),
            expert_support=caps.get("expert_support", False),
            vision_support=caps.get("vision_support", False),
            audio_support=caps.get("audio_support", False),
            tool_support=caps.get("tool_support", False),
            embedding_support=caps.get("embedding_support", False),
            reranking_support=caps.get("reranking_support", False),
            quantization_support=caps.get("quantization_support", False),
            backend_requirements=tuple(caps.get("backend_requirements", ["mlx"])),
            license=license_str,
            repository_metadata=MappingProxyType({}),
            recommended_backend="mlx",
            recommended_quantization="none",
            recommended_execution_mode="batched",
            recommended_scheduler="continuous",
            compatibility_report=MappingProxyType({}),
            validation_report=MappingProxyType({}),
            planner_metadata=MappingProxyType(normalized.get("planner_metadata", {})),
            compiler_metadata=MappingProxyType(normalized.get("compiler_metadata", {}))
        )

        self._cache[cache_key] = descriptor
        return descriptor
