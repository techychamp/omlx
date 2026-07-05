# SPDX-License-Identifier: Apache-2.0
"""
Statistics Collection.
"""

from typing import Dict, Any, List
from omlx.framework.model_intelligence.registry import ModelRegistry

class StatisticsCollector:
    """
    Collects statistics from the registry.
    """
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def collect(self) -> Dict[str, Any]:
        """Collects all statistics."""
        descriptors = self.registry.get_all()

        family_distribution: Dict[str, int] = {}
        architecture_distribution: Dict[str, int] = {}
        capability_distribution: Dict[str, int] = {
            "kv_cache": 0,
            "speculative": 0,
            "streaming": 0,
            "expert": 0,
            "vision": 0,
            "audio": 0,
            "tool": 0,
            "embedding": 0,
            "reranking": 0,
            "quantization": 0
        }

        unknown_capability_count = 0

        for d in descriptors:
            # Family
            family_distribution[d.model_family] = family_distribution.get(d.model_family, 0) + 1

            # Architecture
            architecture_distribution[d.architecture] = architecture_distribution.get(d.architecture, 0) + 1

            # Capabilities
            if d.kv_cache_support: capability_distribution["kv_cache"] += 1
            if d.speculative_support: capability_distribution["speculative"] += 1
            if d.streaming_support: capability_distribution["streaming"] += 1
            if d.expert_support: capability_distribution["expert"] += 1
            if d.vision_support: capability_distribution["vision"] += 1
            if d.audio_support: capability_distribution["audio"] += 1
            if d.tool_support: capability_distribution["tool"] += 1
            if d.embedding_support: capability_distribution["embedding"] += 1
            if d.reranking_support: capability_distribution["reranking"] += 1
            if d.quantization_support: capability_distribution["quantization"] += 1

            # Unknown capability logic (if family/arch are unknown)
            if d.model_family == "Unknown" or d.architecture == "Unknown":
                unknown_capability_count += 1

        return {
             "family_distribution": family_distribution,
             "architecture_distribution": architecture_distribution,
             "capability_distribution": capability_distribution,
             "unknown_capability_count": unknown_capability_count,
             "total_models": len(descriptors)
        }
