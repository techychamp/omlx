# SPDX-License-Identifier: Apache-2.0

import hashlib
from typing import Optional, List
from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.planner.ir.graph import ExecutionIR
from .artifact import CapabilityReport, ExecutionRequirements, AnalysisFingerprint
from .graph import AnalysisGraph
from .cache import AnalysisCache
from .passes.base import AnalysisPass
from .passes.semantic import SemanticAnalysisPass
from .passes.capability import CapabilityPass
from .passes.feature import FeatureDetectionPass
from .passes.requirement import RequirementPass
from .passes.diagnostics import DiagnosticsPass

class AnalysisPipeline:
    """Orchestrates Analysis Passes over the AnalysisGraph."""

    COMPILER_VERSION = "1.0.0"
    ANALYSIS_VERSION = "1.0.0"

    def __init__(self, use_cache: bool = True):
        self.cache = AnalysisCache() if use_cache else None

        # Register Passes
        self.passes: List[AnalysisPass] = [
            SemanticAnalysisPass(),
            CapabilityPass(),
            FeatureDetectionPass(),
            RequirementPass(),
            DiagnosticsPass()
        ]

    def _compute_hash(self, descriptor: ModelDescriptor) -> str:
        # Simplistic hash based on model_id and parameter count
        key = f"{descriptor.model_id}_{descriptor.parameter_count}"
        return hashlib.sha256(key.encode()).hexdigest()

    def analyze(self, descriptor: ModelDescriptor, ir: ExecutionIR) -> CapabilityReport:
        fingerprint = AnalysisFingerprint(
            model_hash=self._compute_hash(descriptor),
            compiler_version=self.COMPILER_VERSION,
            ir_version="1.0.0", # Can be read from IR metadata eventually
            analysis_version=self.ANALYSIS_VERSION
        )

        if self.cache:
            cached_report = self.cache.load(fingerprint)
            if cached_report:
                return cached_report

        graph = AnalysisGraph(descriptor, ir)

        # Execute Passes
        results = {}
        for p in self.passes:
            results.update({type(p).__name__: p.run(graph)})

        semantic_traits = results.get("SemanticAnalysisPass", {})
        capabilities = results.get("CapabilityPass", {})
        features = results.get("FeatureDetectionPass", {})
        reqs = results.get("RequirementPass", {})
        diag = results.get("DiagnosticsPass", {})

        # Merge feature-based dependencies
        dependencies = reqs.get("dependencies", [])
        if "rope" in features:
            dependencies.append("rotary_embedding")
        if "flash_attention" in features:
            dependencies.append("flash_attention")
        if "vision_encoder" in features:
            dependencies.append("vision_encoder")

        requirements = ExecutionRequirements(
            capabilities=capabilities,
            constraints=reqs.get("constraints", {}),
            resources=reqs.get("resources", []),
            dependencies=dependencies,
            features=features,
            semantic_traits=semantic_traits
        )

        report = CapabilityReport(
            fingerprint=fingerprint,
            architecture=descriptor.architecture,
            requirements=requirements,
            unsupported=diag.get("unsupported", [])
        )

        if self.cache:
            self.cache.save(report)

        return report
