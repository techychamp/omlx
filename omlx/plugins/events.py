from dataclasses import dataclass
from .descriptor import PluginLifecycleState

@dataclass(frozen=True)
class PluginEvent:
    plugin_id: str

@dataclass(frozen=True)
class PluginDiscovered(PluginEvent):
    pass

@dataclass(frozen=True)
class PluginLoaded(PluginEvent):
    pass

@dataclass(frozen=True)
class PluginValidated(PluginEvent):
    pass

@dataclass(frozen=True)
class PluginRejected(PluginEvent):
    reason: str

@dataclass(frozen=True)
class DependencyResolved(PluginEvent):
    dependencies: frozenset[str]

@dataclass(frozen=True)
class DependencyFailed(PluginEvent):
    failed_dependency: str
    reason: str

@dataclass(frozen=True)
class PermissionDenied(PluginEvent):
    permission: str
    reason: str

@dataclass(frozen=True)
class TrustViolation(PluginEvent):
    trust_level: str
    reason: str
