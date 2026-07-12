# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict
from .base import AnalysisPass
from ..graph import AnalysisGraph

class CapabilityPass(AnalysisPass):
    """Answers: What user-visible capabilities emerge?"""

    def run(self, graph: AnalysisGraph) -> Dict[str, Any]:
        desc = graph.descriptor

        capabilities = {
            "chat": desc.task in ("chat", "conversational") or desc.tokenizer_family != "",
            "embeddings": desc.embedding_support or desc.task == "embedding",
            "vision": desc.vision_support or desc.modality in ("vision", "multimodal"),
            "audio": desc.audio_support or desc.modality == "audio",
            "diffusion": desc.modality == "image_generation",
            "moe": desc.expert_support or desc.expert_count > 0,
            "speculative_decoding": desc.speculative_support,
            "long_context": desc.context_length >= 32768,
            "streaming": desc.streaming_support,
            "function_calling": desc.tool_support,
            "tool_calling": desc.tool_support,
        }

        # Fallback for moe if routing node exists
        for node in graph.nodes():
            if node.node_type.value == "routing":
                capabilities["moe"] = True

        return capabilities
