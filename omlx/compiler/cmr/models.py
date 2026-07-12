from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set
from omlx.compiler.artifacts import CompilerArtifact

@dataclass
class TensorDescription:
    layers: Optional[int] = None
    hidden_size: Optional[int] = None
    heads: Optional[int] = None
    kv_heads: Optional[int] = None
    rope: Optional[str] = None
    # Add other common tensor metadata here

@dataclass
class TokenizerDescription:
    type: Optional[str] = None
    # Add other tokenizer metadata here

@dataclass
class QuantizationDescription:
    format: Optional[str] = None
    # Add other quantization metadata here

@dataclass
class CapabilityDescription:
    supported_features: Set[str] = field(default_factory=set)

@dataclass
class MultimodalDescription:
    vision_supported: bool = False
    audio_supported: bool = False
    # Add other multimodal metadata here

@dataclass
class GenerationDescription:
    max_context_length: Optional[int] = None
    # Add other generation metadata here

@dataclass
class CanonicalModelRepresentation(CompilerArtifact):
    architecture: str = "unknown"
    cmr_version: int = 1
    tensor_metadata: TensorDescription = field(default_factory=TensorDescription)
    tokenizer_metadata: TokenizerDescription = field(default_factory=TokenizerDescription)
    vocabulary: Dict[str, int] = field(default_factory=dict)
    quantization_metadata: QuantizationDescription = field(default_factory=QuantizationDescription)
    capabilities: CapabilityDescription = field(default_factory=CapabilityDescription)
    special_tokens: Dict[str, int] = field(default_factory=dict)
    multimodal_metadata: MultimodalDescription = field(default_factory=MultimodalDescription)
    generation_metadata: GenerationDescription = field(default_factory=GenerationDescription)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if isinstance(self.capabilities.supported_features, set):
            data['capabilities']['supported_features'] = list(self.capabilities.supported_features)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CanonicalModelRepresentation':
        kwargs = data.copy()

        if 'tensor_metadata' in kwargs and isinstance(kwargs['tensor_metadata'], dict):
            kwargs['tensor_metadata'] = TensorDescription(**kwargs['tensor_metadata'])
        if 'tokenizer_metadata' in kwargs and isinstance(kwargs['tokenizer_metadata'], dict):
            kwargs['tokenizer_metadata'] = TokenizerDescription(**kwargs['tokenizer_metadata'])
        if 'quantization_metadata' in kwargs and isinstance(kwargs['quantization_metadata'], dict):
            kwargs['quantization_metadata'] = QuantizationDescription(**kwargs['quantization_metadata'])
        if 'capabilities' in kwargs and isinstance(kwargs['capabilities'], dict):
            caps = kwargs['capabilities']
            if 'supported_features' in caps and isinstance(caps['supported_features'], list):
                caps['supported_features'] = set(caps['supported_features'])
            kwargs['capabilities'] = CapabilityDescription(**caps)
        if 'multimodal_metadata' in kwargs and isinstance(kwargs['multimodal_metadata'], dict):
            kwargs['multimodal_metadata'] = MultimodalDescription(**kwargs['multimodal_metadata'])
        if 'generation_metadata' in kwargs and isinstance(kwargs['generation_metadata'], dict):
            kwargs['generation_metadata'] = GenerationDescription(**kwargs['generation_metadata'])

        return cls(**kwargs)
