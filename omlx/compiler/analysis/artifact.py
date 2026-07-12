# SPDX-License-Identifier: Apache-2.0
"""
Immutable Artifacts for Model Analysis Compiler.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Tuple
import json
import time

@dataclass(frozen=True)
class AnalysisFingerprint:
    """Provides fingerprinting for cache invalidation."""
    model_hash: str
    compiler_version: str
    ir_version: str
    analysis_version: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_hash": self.model_hash,
            "compiler_version": self.compiler_version,
            "ir_version": self.ir_version,
            "analysis_version": self.analysis_version,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisFingerprint":
        return cls(
            model_hash=data["model_hash"],
            compiler_version=data["compiler_version"],
            ir_version=data["ir_version"],
            analysis_version=data["analysis_version"],
            timestamp=data.get("timestamp", time.time())
        )

@dataclass(frozen=True)
class ExecutionRequirements:
    """Unified object for execution needs."""
    capabilities: MappingProxyType[str, bool] = field(default_factory=lambda: MappingProxyType({}))
    constraints: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    resources: tuple[str, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    features: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    semantic_traits: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        if not isinstance(self.capabilities, MappingProxyType):
            object.__setattr__(self, 'capabilities', MappingProxyType(self.capabilities))
        if not isinstance(self.constraints, MappingProxyType):
            object.__setattr__(self, 'constraints', MappingProxyType(self.constraints))
        if not isinstance(self.features, MappingProxyType):
            object.__setattr__(self, 'features', MappingProxyType(self.features))
        if not isinstance(self.semantic_traits, MappingProxyType):
            object.__setattr__(self, 'semantic_traits', MappingProxyType(self.semantic_traits))
        if not isinstance(self.resources, tuple):
            object.__setattr__(self, 'resources', tuple(self.resources))
        if not isinstance(self.dependencies, tuple):
            object.__setattr__(self, 'dependencies', tuple(self.dependencies))

    def to_dict(self) -> dict[str, Any]:
        return {
            "capabilities": dict(self.capabilities),
            "constraints": dict(self.constraints),
            "resources": list(self.resources),
            "dependencies": list(self.dependencies),
            "features": dict(self.features),
            "semantic_traits": dict(self.semantic_traits)
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionRequirements":
        return cls(
            capabilities=MappingProxyType(data.get("capabilities", {})),
            constraints=MappingProxyType(data.get("constraints", {})),
            resources=tuple(data.get("resources", [])),
            dependencies=tuple(data.get("dependencies", [])),
            features=MappingProxyType(data.get("features", {})),
            semantic_traits=MappingProxyType(data.get("semantic_traits", {}))
        )

@dataclass(frozen=True)
class CapabilityReport:
    """The final contract produced by the AnalysisPipeline."""
    fingerprint: AnalysisFingerprint
    architecture: str
    requirements: ExecutionRequirements
    unsupported: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not isinstance(self.unsupported, tuple):
            object.__setattr__(self, 'unsupported', tuple(self.unsupported))

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint.to_dict(),
            "architecture": self.architecture,
            "requirements": self.requirements.to_dict(),
            "unsupported": list(self.unsupported)
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CapabilityReport":
        return cls(
            fingerprint=AnalysisFingerprint.from_dict(data["fingerprint"]),
            architecture=data["architecture"],
            requirements=ExecutionRequirements.from_dict(data.get("requirements", {})),
            unsupported=tuple(data.get("unsupported", []))
        )
