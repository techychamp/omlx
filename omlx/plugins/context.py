from typing import Any, Dict, List
from .contracts import ExtensionPoint

class PluginContext:
    """
    Strictly immutable context provided to plugins at runtime.
    Provides read-only access to runtime state, feature flags, and registries.
    """
    def __init__(
        self,
        runtime_context: Any,
        feature_flags: Any,
        registries: Any,
        compiler_metadata: Dict[str, Any],
        backend_metadata: Dict[str, Any]
    ):
        self._runtime_context = runtime_context
        self._feature_flags = feature_flags
        self._registries = registries
        self._compiler_metadata = compiler_metadata
        self._backend_metadata = backend_metadata

    @property
    def runtime_context(self) -> Any:
        return self._runtime_context

    @property
    def feature_flags(self) -> Any:
        return self._feature_flags

    @property
    def registries(self) -> Any:
        return self._registries

    @property
    def compiler_metadata(self) -> Dict[str, Any]:
        return self._compiler_metadata

    @property
    def backend_metadata(self) -> Dict[str, Any]:
        return self._backend_metadata


class PluginInitializationContext(PluginContext):
    """
    Writable context provided to plugins ONLY during initialization.
    Allows registering extensions and generating boot-time diagnostics.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registered_extensions: List[ExtensionPoint] = []
        self._diagnostics: Dict[str, Any] = {}

    def register_extension(self, extension: ExtensionPoint) -> None:
        """Register an extension point provided by this plugin."""
        self._registered_extensions.append(extension)

    def get_registered_extensions(self) -> List[ExtensionPoint]:
        """Get the list of extensions registered by this plugin."""
        return self._registered_extensions

    def add_diagnostic(self, key: str, value: Any) -> None:
         self._diagnostics[key] = value

    @property
    def diagnostics(self) -> Dict[str, Any]:
        return self._diagnostics
