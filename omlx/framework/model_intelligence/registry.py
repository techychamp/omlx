# SPDX-License-Identifier: Apache-2.0
"""
Immutable ModelRegistry.

Stores descriptors, allows querying by capability, family, modality, architecture.
Becomes immutable after Runtime initialization.
"""
from typing import Dict, List, Optional
from omlx.framework.model_intelligence.descriptor import ModelDescriptor
import threading

class ModelRegistry:
    """
    Registry for discovered model descriptors.
    """
    def __init__(self):
        self._descriptors: Dict[str, ModelDescriptor] = {}
        self._lock = threading.Lock()
        self._frozen = False

    def register(self, descriptor: ModelDescriptor) -> None:
        """Registers a new descriptor."""
        with self._lock:
            if self._frozen:
                raise RuntimeError("Registry is frozen and cannot accept new registrations.")
            self._descriptors[descriptor.model_id] = descriptor

    def freeze(self) -> None:
        """Freezes the registry, preventing further registrations."""
        with self._lock:
            self._frozen = True

    def get(self, model_id: str) -> Optional[ModelDescriptor]:
        """Gets a descriptor by model_id."""
        with self._lock:
            return self._descriptors.get(model_id)

    def query_by_capability(self, capability: str) -> List[ModelDescriptor]:
        """Queries for models supporting a specific capability."""
        with self._lock:
            return [
                d for d in self._descriptors.values()
                if getattr(d, f"{capability}_support", False)
            ]

    def query_by_family(self, family: str) -> List[ModelDescriptor]:
        """Queries for models by family."""
        with self._lock:
            return [
                d for d in self._descriptors.values()
                if d.model_family == family
            ]

    def query_by_modality(self, modality: str) -> List[ModelDescriptor]:
        """Queries for models by modality."""
        with self._lock:
            return [
                d for d in self._descriptors.values()
                if d.modality == modality
            ]

    def query_by_architecture(self, architecture: str) -> List[ModelDescriptor]:
        """Queries for models by architecture."""
        with self._lock:
            return [
                d for d in self._descriptors.values()
                if d.architecture == architecture
            ]

    def query_by_backend_suitability(self, backend: str) -> List[ModelDescriptor]:
        """Queries for models suitable for a specific backend."""
        with self._lock:
            return [
                d for d in self._descriptors.values()
                if backend in d.backend_requirements
            ]

    def query_by_quantization(self, quantization_supported: bool) -> List[ModelDescriptor]:
        """Queries for models by quantization support."""
        with self._lock:
            return [
                d for d in self._descriptors.values()
                if d.quantization_support == quantization_supported
            ]

    def query_by_license(self, license_name: str) -> List[ModelDescriptor]:
        """Queries for models by license."""
        with self._lock:
            return [
                d for d in self._descriptors.values()
                if d.license == license_name
            ]

    def get_all(self) -> List[ModelDescriptor]:
        """Gets all descriptors."""
        with self._lock:
            return list(self._descriptors.values())
