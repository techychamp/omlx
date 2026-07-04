from typing import Protocol, Any, Dict, runtime_checkable

@runtime_checkable
class ExtensionPoint(Protocol):
    @property
    def extension_id(self) -> str:
        ...

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
