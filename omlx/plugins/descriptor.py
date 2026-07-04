from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Mapping, Tuple
from enum import Enum
from types import MappingProxyType


class PluginCategory(Enum):
    CAPABILITY = "capability"
    VALIDATION = "validation"
    PLANNER = "planner"
    OPTIMIZATION = "optimization"
    LOWERING = "lowering"
    BACKEND = "backend"
    BACKEND_INTELLIGENCE = "backend_intelligence"
    VERIFICATION = "verification"
    TOOLING = "tooling"
    CLI = "cli"
    EXPORTER = "exporter"
    VISUALIZATION = "visualization"
    QUANTIZATION = "quantization"
    DIAGNOSTICS = "diagnostics"


class PluginLifecycleState(Enum):
    DISCOVERED = "discovered"
    REGISTERED = "registered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    VALIDATED = "validated"
    ENABLED = "enabled"
    DISABLED = "disabled"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"
    FAILED = "failed"


@dataclass(frozen=True)
class PluginDescriptor:
    """
    Strictly immutable metadata descriptor for a plugin.
    Lists are converted to tuples and Dicts to MappingProxyType.
    """
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    category: PluginCategory

    # Version compatibility
    supported_compiler_versions: Tuple[str, ...] = field(default_factory=tuple)
    supported_runtime_versions: Tuple[str, ...] = field(default_factory=tuple)

    # Dependencies
    dependencies: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
    optional_dependencies: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))

    # Capabilities and Extension Points
    provided_extension_points: Tuple[str, ...] = field(default_factory=tuple)
    capabilities: Tuple[str, ...] = field(default_factory=tuple)

    # Additional metadata and diagnostics
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        # Deep-freeze mutable structures to enforce strict immutability
        def deep_freeze(obj: Any) -> Any:
            if isinstance(obj, (list, tuple)):
                return tuple(deep_freeze(x) for x in obj)
            elif isinstance(obj, (dict, MappingProxyType)):
                return MappingProxyType({k: deep_freeze(v) for k, v in obj.items()})
            elif isinstance(obj, set):
                return frozenset(deep_freeze(x) for x in obj)
            return obj

        object.__setattr__(self, 'supported_compiler_versions', deep_freeze(self.supported_compiler_versions))
        object.__setattr__(self, 'supported_runtime_versions', deep_freeze(self.supported_runtime_versions))
        object.__setattr__(self, 'dependencies', deep_freeze(self.dependencies))
        object.__setattr__(self, 'optional_dependencies', deep_freeze(self.optional_dependencies))
        object.__setattr__(self, 'provided_extension_points', deep_freeze(self.provided_extension_points))
        object.__setattr__(self, 'capabilities', deep_freeze(self.capabilities))
        object.__setattr__(self, 'metadata', deep_freeze(self.metadata))
        object.__setattr__(self, 'diagnostics', deep_freeze(self.diagnostics))
