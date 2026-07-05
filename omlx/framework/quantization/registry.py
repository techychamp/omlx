# SPDX-License-Identifier: Apache-2.0
"""
Immutable Quantization Registry.
"""

from typing import Dict, List, Optional, Tuple
from .descriptor import QuantizationDescriptor
from .types import QuantizationFamily

class QuantizationRegistry:
    """
    Immutable Quantization Registry.
    Becomes immutable after initialization.
    """
    def __init__(self, descriptors: List[QuantizationDescriptor]):
        self._registry: Dict[str, QuantizationDescriptor] = {}
        for desc in descriptors:
            # We can use quantization family + precisions as a composite key or just track by family for now
            # To be safe we will just store them in a list and provide query methods.
            pass
        self._descriptors = tuple(descriptors)

    def get_all(self) -> Tuple[QuantizationDescriptor, ...]:
        return self._descriptors

    def query_by_family(self, family: QuantizationFamily) -> Tuple[QuantizationDescriptor, ...]:
        return tuple(d for d in self._descriptors if d.quantization_family == family)

    def query_by_precision(self, precision: str) -> Tuple[QuantizationDescriptor, ...]:
        return tuple(d for d in self._descriptors if d.weight_precision == precision or d.compute_precision == precision)

    def query_by_capability(self, capability: str) -> Tuple[QuantizationDescriptor, ...]:
        # Simple string checking on boolean flags
        res = []
        for d in self._descriptors:
            if capability == "streaming" and d.supports_streaming:
                res.append(d)
            elif capability == "batching" and d.supports_batching:
                res.append(d)
            elif capability == "speculative_decoding" and d.supports_speculative_decoding:
                res.append(d)
        return tuple(res)

    def query_by_backend_compatibility(self, backend: str) -> Tuple[QuantizationDescriptor, ...]:
        return tuple(d for d in self._descriptors if backend in d.supported_backends)

    def query_by_model_family(self, model_family: str) -> Tuple[QuantizationDescriptor, ...]:
        return tuple(d for d in self._descriptors if model_family in d.supported_model_families)

    def query_by_storage_precision(self, precision: str) -> Tuple[QuantizationDescriptor, ...]:
        return tuple(d for d in self._descriptors if d.storage_precision == precision)
