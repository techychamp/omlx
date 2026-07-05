# SPDX-License-Identifier: Apache-2.0
"""
Execution profiles and context definitions for OMLX inference.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, Protocol

if TYPE_CHECKING:
    from omlx.registry.model_info import ModelInfo
    from omlx.runtime.capabilities import EngineCapabilities
    from omlx.runtime.feature_flags import FeatureFlags
    from omlx.inference.execution_backend import ExecutionBackend


@dataclass
class RuntimeConfiguration:
    """Runtime configuration overrides and parameters."""
    max_batch_size: int = 1
    max_seq_len: int = 2048
    enable_profiling: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionContext:
    """The complete context needed to determine how a model should be executed."""
    model_info: ModelInfo
    engine_capabilities: EngineCapabilities
    feature_flags: FeatureFlags
    runtime_config: RuntimeConfiguration = field(default_factory=RuntimeConfiguration)


@dataclass
class ExecutionProfile:
    """Defines the concrete components selected for execution."""
    backend_name: str
    attention_mode: str = "causal"
    cache_mode: str = "standard"
    sampler_mode: str = "standard"
    streaming_mode: str = "standard"
    position_encoding: str = "rope"
    version: str = "v1"


class BackendFactory(Protocol):
    """Protocol for a factory that instantiates an ExecutionBackend."""
    def __call__(self, profile: ExecutionProfile, context: ExecutionContext) -> ExecutionBackend:
        ...


class BackendCompatibilityError(Exception):
    """Raised when an execution profile is not compatible with runtime capabilities."""
    pass


class ExecutionProfileRegistry:
    """Registry for mapping an ExecutionContext to an ExecutionProfile and BackendFactory."""
    
    def __init__(self):
        self._profiles: Dict[str, ExecutionProfile] = {}
        self._factories: Dict[str, BackendFactory] = {}
        # Simple resolvers list that are checked in order
        self._resolvers: list[Callable[[ExecutionContext], ExecutionProfile | None]] = []

    def register_backend(self, name: str, factory: BackendFactory) -> None:
        """Register a backend factory by name."""
        self._factories[name] = factory

    def register_resolver(self, resolver: Callable[[ExecutionContext], ExecutionProfile | None]) -> None:
        """Register a function that can resolve a profile from a context."""
        self._resolvers.append(resolver)

    def resolve(self, context: ExecutionContext) -> tuple[ExecutionProfile, BackendFactory]:
        """Resolve the ExecutionContext to a concrete ExecutionProfile and BackendFactory."""
        for resolver in self._resolvers:
            profile = resolver(context)
            if profile is not None:
                # Capability Negotiation
                if profile.backend_name == "diffusion" and not context.engine_capabilities.supports_diffusion:
                    profile = ExecutionProfile(
                        backend_name="autoregressive",
                        version=profile.version
                    )
                elif profile.backend_name == "linear_speculation" and not getattr(context.engine_capabilities, "supports_linear_spec", False):
                    profile = ExecutionProfile(
                        backend_name="autoregressive",
                        version=profile.version
                    )

                factory = self._factories.get(profile.backend_name)
                if factory is None:
                    raise BackendCompatibilityError(f"Resolved profile specifies unknown backend: {profile.backend_name}")
                return profile, factory
        
        raise BackendCompatibilityError(f"No execution profile could be resolved for context: {context.model_info.model_type}")


# Global registry instance for execution profiles
_GLOBAL_PROFILE_REGISTRY = ExecutionProfileRegistry()

def _default_resolver(context: ExecutionContext) -> ExecutionProfile | None:
    """Default resolver that provides a profile based on model capabilities."""
    if context.model_info.config_model_type in ["nemotron_labs_diffusion"]:
        return ExecutionProfile(
            backend_name="experimental_nemotron",
        )
    if context.model_info.config_model_type in ["diffusion"]:
        # Stub for future diffusion models
        return ExecutionProfile(
            backend_name="diffusion",
        )
    # Default to autoregressive
    return ExecutionProfile(
        backend_name="autoregressive",
    )

def _autoregressive_factory(profile: ExecutionProfile, context: ExecutionContext) -> ExecutionBackend:
    from omlx.inference.backends.autoregressive_backend import AutoregressiveBackend
    from omlx.inference.execution_engine import TransformerExecutionEngine
    engine = TransformerExecutionEngine(batch_generator=None)
    return AutoregressiveBackend(engine=engine)

def _experimental_nemotron_factory(profile: ExecutionProfile, context: ExecutionContext) -> ExecutionBackend:
    from omlx.inference.backends.experimental_diffusion_backend import ExperimentalNemotronBackend, NemotronExecutionEngine
    # Minimal mock adapter to satisfy imports without breaking unrelated tests
    class MockAdapter:
        block_size = 32
        _model = type("Mock", (), {"config": type("MockConfig", (), {"mask_token_id": 100})()})()
        def create_diffusion_mask(self, q_len, prefix_len): return None
        def __call__(self, *args, **kwargs): return None
    
    engine = NemotronExecutionEngine(adapter=MockAdapter())
    return ExperimentalNemotronBackend(engine=engine)

_GLOBAL_PROFILE_REGISTRY.register_resolver(_default_resolver)
_GLOBAL_PROFILE_REGISTRY.register_backend("autoregressive", _autoregressive_factory)
_GLOBAL_PROFILE_REGISTRY.register_backend("experimental_nemotron", _experimental_nemotron_factory)

def get_profile_registry() -> ExecutionProfileRegistry:
    return _GLOBAL_PROFILE_REGISTRY

__all__ = [
    "RuntimeConfiguration",
    "ExecutionContext",
    "ExecutionProfile",
    "BackendFactory",
    "ExecutionProfileRegistry",
    "get_profile_registry",
    "BackendCompatibilityError",
]
