# SPDX-License-Identifier: Apache-2.0
"""
ModelDiscoveryFramework implementation.

Responsible for inspecting model metadata, configuration, architecture, and tokenizer
without loading weights.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging

from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.framework.model_intelligence.classifier import ModelClassifier
from omlx.framework.model_intelligence.extractor import CapabilityExtractor
from omlx.framework.model_intelligence.normalizer import MetadataNormalizer

logger = logging.getLogger(__name__)

class ModelDiscoveryFramework:
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

    def inspect(self, model_dir: Path, model_id: str) -> ModelDescriptor:
        """
        Inspects a model directory and returns a unified ModelDescriptor.
        Does not load model weights.
        """
        model_dir = Path(model_dir)

        # 1. Read Raw Metadata
        raw_config = self._read_json(model_dir / "config.json")
        generation_config = self._read_json(model_dir / "generation_config.json")
        tokenizer_config = self._read_json(model_dir / "tokenizer_config.json")

        raw_metadata = {
            "config": raw_config,
            "generation": generation_config,
            "tokenizer": tokenizer_config,
            "model_id": model_id,
            "path": str(model_dir)
        }

        # 2. Normalize Metadata
        normalized = self.normalizer.normalize(raw_metadata)

        # 3. Classify Architecture & Family
        family, arch, task, modality = self.classifier.classify(normalized)

        # 4. Extract Capabilities
        caps = self.extractor.extract(normalized, arch, family)

        # 5. Extract structural stats
        param_count = normalized.get("num_parameters", 0)  # Often missing without loading weights
        hidden_size = normalized.get("hidden_size", 0)
        layer_count = normalized.get("num_hidden_layers", 0)

        # 6. Build Descriptor
        descriptor = ModelDescriptor(
            model_id=model_id,
            model_family=family,
            architecture=arch,
            task=task,
            modality=modality,
            parameter_count=param_count,
            hidden_size=hidden_size,
            layer_count=layer_count,
            attention_type=caps.get("attention_type", "Standard"),
            activation_type=normalized.get("hidden_act", "unknown"),
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
            backend_requirements=tuple(caps.get("backend_requirements", [])),
            planner_metadata=normalized.get("planner_metadata", {}),
            compiler_metadata=normalized.get("compiler_metadata", {})
        )

        return descriptor
