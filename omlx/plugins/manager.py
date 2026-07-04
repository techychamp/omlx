import importlib
import importlib.metadata
import logging
from typing import Dict, List, Optional, Any
from .registry import PluginRegistry
from .context import PluginInitializationContext
from .descriptor import PluginDescriptor, PluginLifecycleState

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Orchestrates the lifecycle of oMLX plugins.
    Does not own the registry, but coordinates discovery, loading, and initialization.
    """
    def __init__(self, registry: PluginRegistry, runtime_context: Any, feature_flags: Any, compiler_metadata=None, backend_metadata=None):
        self._registry = registry
        self._runtime_context = runtime_context
        self._feature_flags = feature_flags
        self._compiler_metadata = compiler_metadata or {}
        self._backend_metadata = backend_metadata or {}

        # Internal tracking of discovered entry points and loaded modules
        self._discovered_entry_points: Dict[str, Any] = {}
        self._loaded_modules: Dict[str, Any] = {}

    @property
    def registry(self) -> PluginRegistry:
        return self._registry

    def discover_plugins(self, entry_point_group: str = "omlx.plugins") -> None:
        """
        Phase 1: Discover plugins using Python's entry_points mechanism.
        Does NOT load modules. Just finds the entry points.
        """
        try:
            entry_points = importlib.metadata.entry_points()
            if hasattr(entry_points, "select"):
                eps = entry_points.select(group=entry_point_group)
            else:
                eps = entry_points.get(entry_point_group, [])

            for ep in eps:
                self._discovered_entry_points[ep.name] = ep
                # Since we don't have the descriptor yet (needs loading), we can't register it in the main registry.
                # The registry tracks plugins by their plugin_id (from descriptor).
        except Exception as e:
            logger.warning(f"Error during plugin discovery: {e}")

    def load_plugins(self) -> None:
        """
        Phase 2: Load the discovered entry points (import modules) and read descriptors.
        Registers descriptors into the PluginRegistry.
        """
        for ep_name, ep in self._discovered_entry_points.items():
            try:
                plugin_module = ep.load()

                if hasattr(plugin_module, "get_descriptor"):
                    descriptor = plugin_module.get_descriptor()
                    if isinstance(descriptor, PluginDescriptor):
                        self._registry.register_plugin(descriptor)
                        self._registry.transition_state(descriptor.plugin_id, PluginLifecycleState.LOADED)
                        self._loaded_modules[descriptor.plugin_id] = plugin_module
                    else:
                        logger.warning(f"Entry point {ep.name} did not return a valid PluginDescriptor")
                else:
                    logger.warning(f"Entry point {ep.name} has no get_descriptor() function")
            except Exception as e:
                logger.error(f"Failed to load plugin from entry point {ep.name}: {e}")

    def initialize_plugins(self) -> None:
        """
        Phase 3: Initialize the loaded modules, giving them the writable InitializationContext.
        """
        for plugin_id, plugin_module in self._loaded_modules.items():
            state = self._registry.get_state(plugin_id)
            if state in (PluginLifecycleState.FAILED, PluginLifecycleState.DISABLED):
                continue

            if hasattr(plugin_module, "initialize_plugin"):
                try:
                    # Create writable initialization context
                    context = PluginInitializationContext(
                        runtime_context=self._runtime_context,
                        feature_flags=self._feature_flags,
                        registries=self._registry,
                        compiler_metadata=self._compiler_metadata,
                        backend_metadata=self._backend_metadata
                    )

                    plugin_module.initialize_plugin(context)

                    # Store registered extensions into the central registry
                    extensions = context.get_registered_extensions()
                    if extensions:
                        self._registry.register_extensions(plugin_id, extensions)

                    self._registry.transition_state(plugin_id, PluginLifecycleState.INITIALIZED)
                except Exception as e:
                    logger.error(f"Failed to initialize plugin {plugin_id}: {e}")
                    self._registry.transition_state(plugin_id, PluginLifecycleState.FAILED)

    def validate_and_seal(self) -> None:
        """
        Phase 4: Validate dependency graph and seal registry.
        """
        self._registry.validate_dependencies()

        # Transition healthy plugins to enabled (if validation passed)
        # We need to access descriptors which is protected, but we can just use the public getter conceptually,
        # or we just iterate the ones we loaded.
        for plugin_id in self._loaded_modules.keys():
            if self._registry.get_state(plugin_id) not in (PluginLifecycleState.FAILED, PluginLifecycleState.DISABLED):
                self._registry.transition_state(plugin_id, PluginLifecycleState.ENABLED)

        self._registry.seal()

    def get_diagnostics(self) -> Dict:
        return self._registry.generate_diagnostics_report()
