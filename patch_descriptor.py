import re

with open('omlx/plugins/descriptor.py', 'r') as f:
    content = f.read()

# Add PluginPriority and PluginCapability
enum_additions = """
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

"""

content = content.replace("class PluginCategory(Enum):", enum_additions + "class PluginCategory(Enum):")

descriptor_mod = """    # Additional metadata and diagnostics
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    priority: PluginPriority = PluginPriority.STANDARD
    configuration: PluginConfiguration = field(default_factory=PluginConfiguration)"""

content = content.replace("""    # Additional metadata and diagnostics
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))""", descriptor_mod)

post_init_mod = """        object.__setattr__(self, 'metadata', deep_freeze(self.metadata))
        object.__setattr__(self, 'diagnostics', deep_freeze(self.diagnostics))
        object.__setattr__(self, 'configuration', deep_freeze(self.configuration))"""

content = content.replace("""        object.__setattr__(self, 'metadata', deep_freeze(self.metadata))
        object.__setattr__(self, 'diagnostics', deep_freeze(self.diagnostics))""", post_init_mod)

with open('omlx/plugins/descriptor.py', 'w') as f:
    f.write(content)
