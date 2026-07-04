from typing import Any
from .descriptor import CapabilityDescriptor, ExecutionFamily, AttentionType, CacheLayoutType
from .exceptions import CapabilityValidationError

def validate_capabilities(caps: dict[str, Any]) -> None:
    """Validate a dictionary of capabilities before conversion to a descriptor."""

    # Check invalid combinations
    family = caps.get("execution_family")
    attention_types = caps.get("attention_types", [])
    cache_layout = caps.get("cache_layout")

    if family == ExecutionFamily.DIFFUSION:
        if caps.get("supports_streaming", False):
            raise CapabilityValidationError("Diffusion models do not support streaming.")
        if AttentionType.CAUSAL in attention_types:
            raise CapabilityValidationError("Diffusion models cannot use causal attention.")

    if family == ExecutionFamily.EMBEDDING:
        if caps.get("supports_streaming", False):
            raise CapabilityValidationError("Embedding models do not support streaming.")

    if family == ExecutionFamily.AUTOREGRESSIVE:
        if AttentionType.DIFFUSION in attention_types:
            raise CapabilityValidationError("Autoregressive models cannot use diffusion attention.")
