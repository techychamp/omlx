from abc import ABC, abstractmethod
from typing import Any
from .descriptor import ExecutionFamily, AttentionType, CacheLayoutType
from .exceptions import CapabilityValidationError

class ValidationRule(ABC):
    @abstractmethod
    def validate(self, caps: dict[str, Any]) -> None:
        pass

class DiffusionStreamingRule(ValidationRule):
    def validate(self, caps: dict[str, Any]) -> None:
        family = caps.get("execution_family")
        if family == ExecutionFamily.DIFFUSION and caps.get("supports_streaming", False):
            raise CapabilityValidationError("Diffusion models do not support streaming.")

class DiffusionAttentionRule(ValidationRule):
    def validate(self, caps: dict[str, Any]) -> None:
        family = caps.get("execution_family")
        attention_types = caps.get("attention_types", [])
        if family == ExecutionFamily.DIFFUSION and AttentionType.CAUSAL in attention_types:
            raise CapabilityValidationError("Diffusion models cannot use causal attention.")

class EmbeddingStreamingRule(ValidationRule):
    def validate(self, caps: dict[str, Any]) -> None:
        family = caps.get("execution_family")
        if family == ExecutionFamily.EMBEDDING and caps.get("supports_streaming", False):
            raise CapabilityValidationError("Embedding models do not support streaming.")

class AutoregressiveAttentionRule(ValidationRule):
    def validate(self, caps: dict[str, Any]) -> None:
        family = caps.get("execution_family")
        attention_types = caps.get("attention_types", [])
        if family == ExecutionFamily.AUTOREGRESSIVE and AttentionType.DIFFUSION in attention_types:
            raise CapabilityValidationError("Autoregressive models cannot use diffusion attention.")

class ValidationRegistry:
    def __init__(self, rules: list[ValidationRule] | None = None):
        # Freeze the rule list to ensure thread-safety
        self._rules: tuple[ValidationRule, ...] = tuple(rules) if rules else tuple()

    @property
    def rules(self) -> tuple[ValidationRule, ...]:
        return self._rules

class ValidationEngine:
    def __init__(self, registry: ValidationRegistry):
        self.registry = registry

    def validate(self, caps: dict[str, Any]) -> None:
        for rule in self.registry.rules:
            rule.validate(caps)

def validate_capabilities(caps: dict[str, Any]) -> None:
    """Validate a dictionary of capabilities before conversion to a descriptor."""
    # Default engine for backward compatibility, although Resolver should instantiate its own
    registry = ValidationRegistry([
        DiffusionStreamingRule(),
        DiffusionAttentionRule(),
        EmbeddingStreamingRule(),
        AutoregressiveAttentionRule()
    ])
    engine = ValidationEngine(registry)
    engine.validate(caps)
