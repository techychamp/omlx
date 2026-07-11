import concurrent.futures
import logging
from typing import Dict, Any, List
from .descriptor import PluginDescriptor, PluginLifecycleState
from .registry import PluginRegistry

logger = logging.getLogger(__name__)

class PluginLoader:
    def __init__(self, registry: PluginRegistry, max_workers: int = 4):
        self._registry = registry
        self._max_workers = max_workers

    def load_parallel(self, entry_points: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loads discovered entry points in parallel and registers their descriptors.
        Returns the loaded modules mapped by plugin_id.
        """
        loaded_modules = {}

        def _load_single(ep_name, ep):
            try:
                plugin_module = ep.load()
                if hasattr(plugin_module, "get_descriptor"):
                    descriptor = plugin_module.get_descriptor()
                    if isinstance(descriptor, PluginDescriptor):
                        return (ep_name, descriptor, plugin_module)
                    else:
                        logger.warning(f"Entry point {ep_name} did not return a valid PluginDescriptor")
                else:
                    logger.warning(f"Entry point {ep_name} has no get_descriptor() function")
            except Exception as e:
                logger.error(f"Failed to load plugin from entry point {ep_name}: {e}")
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [executor.submit(_load_single, ep_name, ep) for ep_name, ep in entry_points.items()]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    ep_name, descriptor, module = result
                    self._registry.register_plugin(descriptor)
                    self._registry.transition_state(descriptor.plugin_id, PluginLifecycleState.LOADED)
                    loaded_modules[descriptor.plugin_id] = module

        return loaded_modules
