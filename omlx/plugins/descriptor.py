from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Mapping, Tuple
from enum import Enum
from types import MappingProxyType



class PluginPriority(Enum):
    CORE = 0
    BUILT_IN = 1
    PREFERRED = 2
    STANDARD = 3
    OPTIONAL = 4
    EXPERIMENTAL = 5
    DEVELOPER_OVERRIDE = 6

class PluginCapability(Enum):
    COMPILER_EXTENSION = "compiler_extension"
    PLANNER_EXTENSION = "planner_extension"
    OPTIMIZATION_EXTENSION = "optimization_extension"
    LOWERING_EXTENSION = "lowering_extension"
    BACKEND_EXTENSION = "backend_extension"
    VERIFICATION_EXTENSION = "verification_extension"
    TOOLING_EXTENSION = "tooling_extension"
    CLI_EXTENSION = "cli_extension"
    VISUALIZATION_EXTENSION = "visualization_extension"
    EXPORTER_EXTENSION = "exporter_extension"
    QUANTIZATION_EXTENSION = "quantization_extension"

class PluginPermission(Enum):
    COMPILER_ACCESS = "compiler_access"
    PLANNER_ACCESS = "planner_access"
    BACKEND_ACCESS = "backend_access"
    VERIFICATION_ACCESS = "verification_access"
    TOOLING_ACCESS = "tooling_access"
    FILESYSTEM_READ = "filesystem_read"
    FILESYSTEM_WRITE = "filesystem_write"
    NETWORK_ACCESS = "network_access"
    CONFIGURATION_ACCESS = "configuration_access"
    DIAGNOSTICS_ACCESS = "diagnostics_access"

class PluginTrustLevel(Enum):
    CORE = "core"
    BUILT_IN = "built_in"
    VERIFIED = "verified"
    SIGNED = "signed"
    THIRD_PARTY = "third_party"
    EXPERIMENTAL = "experimental"
    DEVELOPER = "developer"
    UNTRUSTED = "untrusted"

@dataclass(frozen=True)
class PluginIsolationPolicy:
    shared_state_allowed: bool = False
    read_only_context: bool = True
    exclusive_extension_point: bool = False
    stateless_only: bool = True
    thread_safe_required: bool = True
    future_sandbox_capable: bool = True

@dataclass(frozen=True)
class PluginConfiguration:
    enabled: bool = True
    disabled: bool = False
    priority: PluginPriority = PluginPriority.STANDARD
    configuration_values: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    feature_flags: Tuple[str, ...] = field(default_factory=tuple)
    plugin_metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    configuration_diagnostics: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self):
        def deep_freeze(obj: Any) -> Any:
            if isinstance(obj, (list, tuple)):
                return tuple(deep_freeze(x) for x in obj)
            elif isinstance(obj, (dict, MappingProxyType)):
                return MappingProxyType({k: deep_freeze(v) for k, v in obj.items()})
            elif isinstance(obj, set):
                return frozenset(deep_freeze(x) for x in obj)
            return obj

        object.__setattr__(self, 'configuration_values', deep_freeze(self.configuration_values))
        object.__setattr__(self, 'feature_flags', deep_freeze(self.feature_flags))
        object.__setattr__(self, 'plugin_metadata', deep_freeze(self.plugin_metadata))
        object.__setattr__(self, 'configuration_diagnostics', deep_freeze(self.configuration_diagnostics))

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

    # Security & Trust
    permissions: Tuple[PluginPermission, ...] = field(default_factory=tuple)
    trust_level: PluginTrustLevel = PluginTrustLevel.UNTRUSTED
    isolation_policy: PluginIsolationPolicy = field(default_factory=PluginIsolationPolicy)

    # Capability Restrictions
    required_compiler_stages: Tuple[str, ...] = field(default_factory=tuple)
    supported_backend_families: Tuple[str, ...] = field(default_factory=tuple)
    supported_execution_families: Tuple[str, ...] = field(default_factory=tuple)
    required_feature_flags: Tuple[str, ...] = field(default_factory=tuple)
    required_optimization_phases: Tuple[str, ...] = field(default_factory=tuple)

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

    priority: PluginPriority = PluginPriority.STANDARD
    configuration: PluginConfiguration = field(default_factory=PluginConfiguration)

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

        object.__setattr__(self, 'permissions', deep_freeze(self.permissions))
        object.__setattr__(self, 'required_compiler_stages', deep_freeze(self.required_compiler_stages))
        object.__setattr__(self, 'supported_backend_families', deep_freeze(self.supported_backend_families))
        object.__setattr__(self, 'supported_execution_families', deep_freeze(self.supported_execution_families))
        object.__setattr__(self, 'required_feature_flags', deep_freeze(self.required_feature_flags))
        object.__setattr__(self, 'required_optimization_phases', deep_freeze(self.required_optimization_phases))
        object.__setattr__(self, 'supported_compiler_versions', deep_freeze(self.supported_compiler_versions))
        object.__setattr__(self, 'supported_runtime_versions', deep_freeze(self.supported_runtime_versions))
        object.__setattr__(self, 'dependencies', deep_freeze(self.dependencies))
        object.__setattr__(self, 'optional_dependencies', deep_freeze(self.optional_dependencies))
        object.__setattr__(self, 'provided_extension_points', deep_freeze(self.provided_extension_points))
        object.__setattr__(self, 'capabilities', deep_freeze(self.capabilities))
        object.__setattr__(self, 'metadata', deep_freeze(self.metadata))
        object.__setattr__(self, 'diagnostics', deep_freeze(self.diagnostics))
        object.__setattr__(self, 'configuration', deep_freeze(self.configuration))
