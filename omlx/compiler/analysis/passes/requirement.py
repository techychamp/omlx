# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict, List, Set, Tuple
from .base import AnalysisPass
from ..graph import AnalysisGraph

class RequirementPass(AnalysisPass):
    """Identifies constraints, resources, and dependencies."""

    def run(self, graph: AnalysisGraph) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {}
        resources: Set[str] = set()
        dependencies: Set[str] = set()

        desc = graph.descriptor

        # Constraints
        if desc.parameter_count > 0:
            bytes_required = desc.parameter_count * 2 * 1.2
            gb_required = bytes_required / (1024 ** 3)
            constraints["minimum_memory"] = f"{gb_required:.1f}GB"

        if desc.context_length > 0:
            constraints["maximum_sequence_length"] = desc.context_length

        if desc.backend_requirements:
            constraints["preferred_backend"] = desc.backend_requirements[0]

        required_precisions = set()
        for node in graph.nodes():
            if "precision" in node.metadata:
                required_precisions.add(node.metadata["precision"])
            if node.metadata.get("dynamic_shapes", False):
                constraints["dynamic_shapes"] = True

        if required_precisions:
            constraints["required_precision"] = list(required_precisions)

        # Dependencies / Resources
        if desc.kv_cache_support:
            dependencies.add("kv_cache")
        if desc.tokenizer_family:
            dependencies.add("tokenizer")
        if desc.task in ("chat", "text_generation"):
            dependencies.add("sampling")

        # The pipeline can merge features output into dependencies
        # e.g., if 'rope' in features, add 'rotary_embedding'
        # We will handle feature-based dependencies in the pipeline orchestration

        return {
            "constraints": constraints,
            "resources": list(resources),
            "dependencies": list(dependencies)
        }
