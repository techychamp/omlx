from typing import Protocol, Any, Dict, List, Tuple, runtime_checkable
from .descriptor import PluginCapability

@runtime_checkable
class ExtensionPoint(Protocol):
    @property
    def extension_id(self) -> str:
        ...

    @property
    def display_name(self) -> str:
        return self.extension_id

    @property
    def description(self) -> str:
        return ""

    @property
    def plugin_owner(self) -> str:
        return ""

    @property
    def supported_compiler_stages(self) -> Tuple[str, ...]:
        return ()

    @property
    def supported_backend_families(self) -> Tuple[str, ...]:
        return ()

    @property
    def supported_execution_families(self) -> Tuple[str, ...]:
        return ()

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def capabilities(self) -> Tuple[PluginCapability, ...]:
        return ()

    @property
    def diagnostics(self) -> Dict[str, Any]:
        return {}

@runtime_checkable
class CapabilityPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class PlannerPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class OptimizationPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class LoweringPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class BackendPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class BackendIntelligencePlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class VerificationPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class ToolingPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class CLIPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class ExporterPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class VisualizationPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class QuantizationPlugin(ExtensionPoint, Protocol):
    pass

@runtime_checkable
class DiagnosticsPlugin(ExtensionPoint, Protocol):
    pass
