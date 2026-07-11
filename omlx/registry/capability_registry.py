# SPDX-License-Identifier: Apache-2.0
"""
Registry for generation strategies and capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from omlx.inference.attention import AttentionMode
    from omlx.inference.modes import GenerationMode
    from omlx.inference.strategy import BaseGenerationStrategy
    from omlx.runtime.capabilities import ActualCapabilities


__all__ = [
    "CacheHints",
    "SchedulerHooks",
    "UIMetadata",
    "RuntimeRequirements",
    "CapabilityBundle",
    "GenerationStrategyRegistry",
]


@dataclass
class CacheHints:
    """Hints for cache configuration."""
    preferred_block_size: int | None = None
    supports_shared_prefix: bool = False
    supports_partial_accept: bool = False
    supports_cache_transition: bool = False


@dataclass
class SchedulerHooks:
    """Callables the Scheduler invokes around its step() phases."""
    on_request_admitted: Callable | None = None
    on_prefill_start: Callable | None = None
    on_prefill_done: Callable | None = None
    on_decode_step: Callable | None = None
    on_request_finished: Callable | None = None


@dataclass
class UIMetadata:
    """Metadata for UI rendering."""
    display_name: str
    description: str
    experimental: bool = False
    icon: str = ""


@dataclass
class RuntimeRequirements:
    """Requirements for the strategy to run."""
    minimum_memory: int = 0
    preferred_cache: str | None = None
    required_attention: list[AttentionMode] | None = None
    requires_bidirectional: bool = False
    supports_streaming: bool = True
    supports_continuous_batching: bool = True


@dataclass
class CapabilityBundle:
    """A complete bundle of capabilities for a generation strategy."""
    mode: GenerationMode
    strategy_class: type[BaseGenerationStrategy]
    attention_modes: list[AttentionMode]
    cache_hints: CacheHints
    scheduler_hooks: SchedulerHooks
    ui_metadata: UIMetadata
    runtime_requirements: RuntimeRequirements = field(default_factory=RuntimeRequirements)


class GenerationStrategyRegistry:
    """Registry for capability bundles.
    
    This is instantiated per-engine, NOT as a global singleton.
    """
    def __init__(self) -> None:
        self._bundles: dict[GenerationMode, CapabilityBundle] = {}

    def register(self, bundle: CapabilityBundle) -> None:
        """Register a new capability bundle."""
        self._bundles[bundle.mode] = bundle

    def get_bundle(self, mode: GenerationMode) -> CapabilityBundle:
        """Get the capability bundle for a generation mode."""
        if mode not in self._bundles:
            raise KeyError(f"No strategy registered for mode {mode}")
        return self._bundles[mode]

    def get_strategy_class(self, mode: GenerationMode) -> type[BaseGenerationStrategy]:
        """Get the strategy class for a generation mode."""
        return self.get_bundle(mode).strategy_class

    def resolve_mode(self, capabilities: ActualCapabilities) -> GenerationMode:
        """Return best GenerationMode for the given ActualCapabilities."""
        # Simple resolution logic for Phase 1
        from omlx.inference.modes import GenerationMode
        from omlx.inference.execution_profile import BackendCompatibilityError
        
        if capabilities.supports_diffusion and GenerationMode.DIFFUSION in self._bundles:
            return GenerationMode.DIFFUSION
        if capabilities.supports_linear_speculation and GenerationMode.LINEAR_SPECULATION in self._bundles:
            return GenerationMode.LINEAR_SPECULATION
            
        if capabilities.supports_autoregressive and GenerationMode.AUTOREGRESSIVE in self._bundles:
            return GenerationMode.AUTOREGRESSIVE
            
        raise BackendCompatibilityError("No compatible generation mode found for the given capabilities.")


def register_default_strategies(registry: GenerationStrategyRegistry) -> None:
    """Register the built-in strategies into a registry instance."""
    from omlx.inference.attention import AttentionMode
    from omlx.inference.modes import GenerationMode
    from omlx.inference.strategies.autoregressive import AutoregressiveStrategy
    from omlx.inference.strategies.diffusion import DiffusionStrategy
    from omlx.inference.strategies.linear_speculation import LinearSpeculationStrategy

    registry.register(CapabilityBundle(
        mode=GenerationMode.AUTOREGRESSIVE,
        strategy_class=AutoregressiveStrategy,
        attention_modes=[AttentionMode.CAUSAL],
        cache_hints=CacheHints(supports_shared_prefix=True, supports_partial_accept=False),
        scheduler_hooks=SchedulerHooks(),
        ui_metadata=UIMetadata("Autoregressive", "Standard token-by-token generation"),
    ))
    
    registry.register(CapabilityBundle(
        mode=GenerationMode.DIFFUSION,
        strategy_class=DiffusionStrategy,
        attention_modes=[AttentionMode.DIFFUSION],
        cache_hints=CacheHints(supports_shared_prefix=False, supports_partial_accept=True),
        scheduler_hooks=SchedulerHooks(),
        ui_metadata=UIMetadata("Diffusion", "Block-parallel diffusion decoding", experimental=True),
    ))
    
    registry.register(CapabilityBundle(
        mode=GenerationMode.LINEAR_SPECULATION,
        strategy_class=LinearSpeculationStrategy,
        attention_modes=[AttentionMode.CAUSAL, AttentionMode.VERIFY],
        cache_hints=CacheHints(supports_shared_prefix=True, supports_partial_accept=True),
        scheduler_hooks=SchedulerHooks(),
        ui_metadata=UIMetadata("Linear Speculation", "Speculative decoding with linear draft", experimental=True),
    ))
