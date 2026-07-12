# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict
from .base import AnalysisPass
from ..graph import AnalysisGraph

class FeatureDetectionPass(AnalysisPass):
    """Detects architectural features by walking the AnalysisGraph."""

    def run(self, graph: AnalysisGraph) -> Dict[str, Any]:
        features = {}

        desc = graph.descriptor
        if desc.attention_type:
            features["attention_type"] = desc.attention_type
            if desc.attention_type == "gqa":
                features["gqa"] = True

        if desc.moe_information:
            features["moe_routing"] = True

        if desc.vision_support:
            features["vlm"] = True
            features["vision_encoder"] = True

        if desc.audio_support:
            features["audio_encoder"] = True

        has_attention = False

        # Traverse IR like an LLVM Pass
        for node in graph.nodes():
            if node.node_type.value == "attention":
                has_attention = True
                if node.metadata.get("flash_attention", False):
                    features["flash_attention"] = True
                if node.metadata.get("rope", False):
                    features["rope"] = node.metadata.get("rope_type", "static")
                if node.metadata.get("sliding_window", False):
                    features["sliding_window"] = True
                if node.metadata.get("cross_attention", False):
                    features["cross_attention"] = True
            elif node.node_type.value == "routing":
                features["moe_routing"] = True
            elif node.node_type.value == "diffusion":
                features["diffusion_blocks"] = True

        if has_attention and "rope" not in features and desc.architecture in ("llama", "mistral", "qwen", "gemma"):
            features["rope"] = "static"

        return features
