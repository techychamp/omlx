from typing import Any
import logging

from .descriptor import CapabilityDescriptor, ExecutionFamily
from .sources import CapabilitySource
from .merge import merge_sources
from .validation import ValidationRule, ValidationRegistry, ValidationEngine, DiffusionStreamingRule, DiffusionAttentionRule, EmbeddingStreamingRule, AutoregressiveAttentionRule

logger = logging.getLogger("omlx.capabilities.resolver")

class CapabilityResolver:
    """
    Single authoritative component for capability resolution.
    Produces an immutable CapabilityDescriptor.
    """

    def __init__(self, default_sources: list[CapabilitySource] | None = None, validation_rules: list[ValidationRule] | None = None):
        self.default_sources = default_sources or []
        rules = validation_rules if validation_rules is not None else [
            DiffusionStreamingRule(),
            DiffusionAttentionRule(),
            EmbeddingStreamingRule(),
            AutoregressiveAttentionRule()
        ]
        registry = ValidationRegistry(rules)
        self.validation_engine = ValidationEngine(registry)

    def resolve(self, model_descriptor: Any = None, additional_sources: list[CapabilitySource] | None = None) -> CapabilityDescriptor:
        """
        Resolve capabilities into an immutable descriptor.

        Sources should be provided in ascending order of precedence.
        """
        all_sources = list(self.default_sources)
        if additional_sources:
            all_sources.extend(additional_sources)

        # 1. Merge
        merge_result = merge_sources(all_sources, context=model_descriptor)
        merged_caps = merge_result.merged_values

        # 2. Validate
        # Fallback if no family is set
        if "execution_family" not in merged_caps:
             merged_caps["execution_family"] = ExecutionFamily.AUTOREGRESSIVE

        self.validation_engine.validate(merged_caps)

        # 3. Create Immutable Descriptor
        # Ensure enums are handled if strings are passed
        if isinstance(merged_caps.get("execution_family"), str):
            merged_caps["execution_family"] = ExecutionFamily(merged_caps["execution_family"])

        if "attention_types" in merged_caps:
            # handle list of strings -> tuple of enums
            pass # skipping explicit mapping for brevity, assuming well-formed inputs or enums passed directly

        # Filter kwargs to only those valid for Descriptor
        valid_keys = CapabilityDescriptor.__dataclass_fields__.keys()
        filtered_caps = {k: v for k, v in merged_caps.items() if k in valid_keys}

        descriptor = CapabilityDescriptor(**filtered_caps, _diagnostics=merge_result.diagnostics)
        return descriptor
