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
        license_distribution: Dict[str, int] = {}
        backend_recommendation_distribution: Dict[str, int] = {}
        compatibility_statistics: Dict[str, int] = {
            "runtime": 0,
            "compiler": 0,
            "backend": 0,
        }

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

        unknown_architecture_count = 0

        for d in descriptors:
            # Family
            family_distribution[d.model_family] = family_distribution.get(d.model_family, 0) + 1

            # Architecture
            architecture_distribution[d.architecture] = architecture_distribution.get(d.architecture, 0) + 1
            if d.architecture == "Unknown":
                unknown_architecture_count += 1

            # License
            license_distribution[d.license] = license_distribution.get(d.license, 0) + 1

            # Recommendations
            backend_recommendation_distribution[d.recommended_backend] = backend_recommendation_distribution.get(d.recommended_backend, 0) + 1

            # Compatibility
            # Since CompatibilityAnalyzer is separate, we'd normally pass the report, but we'll simulate for now based on what descriptor has (which is empty in this context until populated)
            # We assume it is populated by discovery
            report = d.compatibility_report
            if report.get("runtime_compatible", True): compatibility_statistics["runtime"] += 1
            if report.get("compiler_compatible", True): compatibility_statistics["compiler"] += 1
            if report.get("backend_compatible", True): compatibility_statistics["backend"] += 1

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


        return {
             "family_distribution": family_distribution,
             "architecture_distribution": architecture_distribution,
             "license_distribution": license_distribution,
             "backend_recommendation_distribution": backend_recommendation_distribution,
             "capability_distribution": capability_distribution,
             "compatibility_statistics": compatibility_statistics,
             "unknown_architecture_count": unknown_architecture_count,
             "total_models": len(descriptors)
        }
