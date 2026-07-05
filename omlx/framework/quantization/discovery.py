# SPDX-License-Identifier: Apache-2.0
"""
Quantization Discovery Framework.
"""

from typing import Dict, Any, Optional
from .descriptor import QuantizationDescriptor
from .types import QuantizationFamily
from .normalizer import QuantizationNormalizer

class QuantizationDiscoveryFramework:
    """
    Discovers quantization metadata without loading weights.
    """
    def __init__(self):
        self._normalizer = QuantizationNormalizer()

    def discover_from_mlx(self, metadata: Dict[str, Any]) -> Optional[QuantizationDescriptor]:
        return self._normalizer.normalize_mlx(metadata)

    def discover_from_gguf(self, metadata: Dict[str, Any]) -> Optional[QuantizationDescriptor]:
        return self._normalizer.normalize_gguf(metadata)

    def discover_from_safetensors(self, metadata: Dict[str, Any]) -> Optional[QuantizationDescriptor]:
        return self._normalizer.normalize_safetensors(metadata)

    def discover_from_hf(self, config: Dict[str, Any]) -> Optional[QuantizationDescriptor]:
        return self._normalizer.normalize_hf(config)
