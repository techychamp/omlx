# SPDX-License-Identifier: Apache-2.0
"""
Diagnostics generation.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.framework.model_intelligence.registry import ModelRegistry

@dataclass(frozen=True)
class ModelDiagnostic:
    """Structured, passive diagnostic for a model."""
    severity: str # "INFO", "WARNING", "ERROR"
    category: str # e.g., "Architecture", "Capability", "Compatibility"
    component: str # e.g., "ModelClassifier", "CompatibilityAnalyzer"
    message: str
    recommendation: str
    metadata: Dict[str, Any]

class DiagnosticsGenerator:
    """
    Generates reports based on descriptors and the registry.
    """
    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def generate_diagnostics(self, model_id: str) -> List[ModelDiagnostic]:
        """Generates a list of structured diagnostics for a specific model."""
        descriptor = self.registry.get(model_id)
        if not descriptor:
            return [ModelDiagnostic(
                severity="ERROR",
                category="Discovery",
                component="Registry",
                message=f"Model {model_id} not found in registry.",
                recommendation="Ensure model is discovered and registered.",
                metadata={"model_id": model_id}
            )]

        diagnostics = []

        # Check architecture
        if descriptor.architecture == "Unknown":
            diagnostics.append(ModelDiagnostic(
                severity="WARNING",
                category="Architecture",
                component="ModelClassifier",
                message="Unknown architecture detected.",
                recommendation="Add support for this architecture in ModelClassifier.",
                metadata={"model_id": model_id}
            ))

        # Check compatibility
        report = descriptor.compatibility_report
        if not report.get("runtime_compatible", True):
             diagnostics.append(ModelDiagnostic(
                severity="ERROR",
                category="Compatibility",
                component="CompatibilityAnalyzer",
                message="Model is not compatible with the Runtime.",
                recommendation=report.get("details", {}).get("reason", "Check compatibility details."),
                metadata={"model_id": model_id}
            ))

        return diagnostics

    def generate_model_summary(self, model_id: str) -> Dict[str, Any]:
        """Generates a summary for a specific model."""
        descriptor = self.registry.get(model_id)
        if not descriptor:
             return {"error": f"Model {model_id} not found."}

        return {
            "model_id": descriptor.model_id,
            "family": descriptor.model_family,
            "architecture": descriptor.architecture,
            "task": descriptor.task,
            "modality": descriptor.modality,
            "parameters": descriptor.parameter_count
        }

    def generate_capability_report(self, model_id: str) -> Dict[str, Any]:
         """Generates a capability report for a specific model."""
         descriptor = self.registry.get(model_id)
         if not descriptor:
              return {"error": f"Model {model_id} not found."}

         return {
             "kv_cache": descriptor.kv_cache_support,
             "speculative": descriptor.speculative_support,
             "streaming": descriptor.streaming_support,
             "expert": descriptor.expert_support,
             "vision": descriptor.vision_support,
             "audio": descriptor.audio_support,
             "tool": descriptor.tool_support,
             "embedding": descriptor.embedding_support,
             "reranking": descriptor.reranking_support,
             "quantization": descriptor.quantization_support
         }

    def generate_architecture_report(self) -> Dict[str, Any]:
         """Generates a report summarizing architectures in the registry."""
         descriptors = self.registry.get_all()

         arch_counts: Dict[str, int] = {}
         for d in descriptors:
             arch = d.architecture
             arch_counts[arch] = arch_counts.get(arch, 0) + 1

         return {
             "total_models": len(descriptors),
             "architectures": arch_counts
         }

    def generate_discovery_report(self) -> Dict[str, Any]:
        """Generates a high-level discovery report."""
        descriptors = self.registry.get_all()
        return {
            "total_discovered": len(descriptors),
            "families": list(set(d.model_family for d in descriptors)),
            "tasks": list(set(d.task for d in descriptors))
        }
