from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from types import MappingProxyType

from omlx.utils.freezer import deep_freeze as freeze_value


class ExecutionFamily(str, Enum):
    AUTOREGRESSIVE = "autoregressive"
    DIFFUSION = "diffusion"
    TRIAGE = "triage"
    STREAMING_MOE = "streaming_moe"
    EMBEDDING = "embedding"
    VISION = "vision"
    AUDIO = "audio"

class AttentionType(str, Enum):
    CAUSAL = "causal"
    BIDIRECTIONAL = "bidirectional"
    DIFFUSION = "diffusion"
    SLIDING_WINDOW = "sliding_window"
    VERIFY = "verify"
    PREFIX = "prefix"

class CacheLayoutType(str, Enum):
    PAGED = "paged"
    CONTINUOUS = "continuous"
    RADIX_TREE = "radix_tree"
    NONE = "none"

@dataclass(frozen=True)
class CapabilityDescriptor:
    """Immutable snapshot of merged capabilities."""

    execution_family: ExecutionFamily
    supported_modalities: tuple[str, ...] = ("text",)

    attention_types: tuple[AttentionType, ...] = (AttentionType.CAUSAL,)
    cache_layout: CacheLayoutType = CacheLayoutType.PAGED

    # Feature capabilities
    supports_streaming: bool = True
    supports_speculative: bool = False
    supports_diffusion: bool = False
    supports_embedding: bool = False
    supports_verification: bool = False

    # Hardware & constraints
    hardware_requirements: tuple[str, ...] = tuple()
    execution_hints: dict[str, Any] = field(default_factory=dict)

    # Internal diagnostics for provenance tracking. Not part of the public API.
    _diagnostics: dict[str, Any] | None = field(default=None, repr=False, hash=False, compare=False)

    def __post_init__(self):
        for field_name in self.__dataclass_fields__:
            val = getattr(self, field_name)
            object.__setattr__(self, field_name, freeze_value(val))
