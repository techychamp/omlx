# SPDX-License-Identifier: Apache-2.0
"""
Quantization Metadata Normalizer.
"""

from typing import Dict, Any, Optional, Tuple
from types import MappingProxyType
from .descriptor import QuantizationDescriptor
from .types import QuantizationFamily, ValidationStatus
from .classifier import QuantizationClassifier
from .extractor import QuantizationCapabilityExtractor

class QuantizationNormalizer:
    """
    Normalizes metadata from multiple formats into one canonical descriptor.
    """
    def __init__(self):
        self._classifier = QuantizationClassifier()
        self._extractor = QuantizationCapabilityExtractor()

    def _create_descriptor(self, metadata: Dict[str, Any], family: QuantizationFamily, format_type: str) -> QuantizationDescriptor:
        capabilities = self._extractor.extract(metadata, family)
        return QuantizationDescriptor(
            quantization_family=family,
            storage_precision=capabilities.get("storage_precision", "unknown"),
            compute_precision=capabilities.get("compute_precision", "unknown"),
            weight_precision=capabilities.get("weight_precision", "unknown"),
            activation_precision=capabilities.get("activation_precision", "unknown"),
            kv_cache_precision=capabilities.get("kv_cache_precision", "unknown"),
            group_size=capabilities.get("group_size"),
            block_size=capabilities.get("block_size"),
            mixed_precision=capabilities.get("mixed_precision", False),
            dynamic_quantization=capabilities.get("dynamic_quantization", False),
            static_quantization=capabilities.get("static_quantization", False),
            per_channel=capabilities.get("per_channel", False),
            per_group=capabilities.get("per_group", False),
            supports_streaming=capabilities.get("streaming_support", False),
            supports_batching=capabilities.get("batching_support", False),
            supports_speculative_decoding=capabilities.get("speculative_support", False),
            supported_backends=capabilities.get("backend_compatibility", tuple()),
            supported_model_families=capabilities.get("model_compatibility", tuple()),
            packing_information=capabilities.get("packing_information"),
            compression_metadata=MappingProxyType(capabilities.get("compression_metadata", {})),
            required_kernels=capabilities.get("required_kernels", tuple()),
            hardware_requirements=capabilities.get("hardware_requirements", tuple()),
            validation_status=capabilities.get("validation_status", ValidationStatus.UNKNOWN),
            metadata=MappingProxyType(metadata),
            planner_metadata=MappingProxyType({}),
            compiler_metadata=MappingProxyType({}),
            backend_metadata=MappingProxyType({})
        )


    def normalize_mlx(self, metadata: Dict[str, Any]) -> QuantizationDescriptor:
        family = self._classifier.classify_mlx(metadata)
        return self._create_descriptor(metadata, family, "mlx")

    def normalize_gguf(self, metadata: Dict[str, Any]) -> QuantizationDescriptor:
        family = self._classifier.classify_gguf(metadata)
        return self._create_descriptor(metadata, family, "gguf")

    def normalize_safetensors(self, metadata: Dict[str, Any]) -> QuantizationDescriptor:
        family = self._classifier.classify_safetensors(metadata)
        return self._create_descriptor(metadata, family, "safetensors")

    def normalize_hf(self, config: Dict[str, Any]) -> QuantizationDescriptor:
        family = self._classifier.classify_hf(config)
        return self._create_descriptor(config, family, "hf")
