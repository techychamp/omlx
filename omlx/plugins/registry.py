import threading
from typing import Dict, List, Optional, Type, Any, Set
from .descriptor import PluginDescriptor, PluginLifecycleState
from .contracts import ExtensionPoint
from .versioning import SemanticVersion

class PluginRegistry:
    """
    Registry for managing plugin discovery, registration, and lifecycle.
    Becomes immutable after startup.
    """
    def __init__(self):
        self._lock = threading.RLock()

        # Map of plugin ID -> PluginDescriptor
        self._descriptors: Dict[str, PluginDescriptor] = {}

        # Map of plugin ID -> Lifecycle State
        self._plugin_states: Dict[str, PluginLifecycleState] = {}

        # Map of Extension Class -> List of registered extension instances
        # We explicitly store extensions here instead of extracting them from contexts
        self._extensions_by_type: Dict[Type[ExtensionPoint], List[ExtensionPoint]] = {}
        # Also store extensions by plugin_id for bookkeeping if necessary
        self._extensions_by_plugin: Dict[str, List[ExtensionPoint]] = {}

        self._is_sealed = False

        # Diagnostics reports
        self._diagnostics: Dict[str, Any] = {
            "registration": {},
            "dependency": {},
            "validation": {},
            "compatibility": {},
            "lifecycle": {},
            "health": {},
            "discovery": {},
            "security": {},
            "trust": {},
            "permission": {}
        }

    def _check_sealed(self):
        if self._is_sealed:
            raise RuntimeError("PluginRegistry is sealed and cannot be modified.")

    def seal(self) -> None:
        """Lock the registry to prevent further modification after startup."""
        with self._lock:
            self._is_sealed = True

    def register_plugin(self, descriptor: PluginDescriptor) -> None:
        """Register a plugin with its descriptor."""
        with self._lock:
            self._check_sealed()

            if descriptor.plugin_id in self._descriptors:
                self._diagnostics["registration"][descriptor.plugin_id] = "Duplicate plugin ID detected."
                raise ValueError(f"Plugin ID {descriptor.plugin_id} is already registered.")

            self._descriptors[descriptor.plugin_id] = descriptor
            self._plugin_states[descriptor.plugin_id] = PluginLifecycleState.REGISTERED
            self._extensions_by_plugin[descriptor.plugin_id] = []
            self._diagnostics["registration"][descriptor.plugin_id] = "Success"
            self._diagnostics["lifecycle"][descriptor.plugin_id] = PluginLifecycleState.REGISTERED.value

    def register_extensions(self, plugin_id: str, extensions: List[ExtensionPoint]) -> None:
        """Register instantiated extensions for a plugin."""
        with self._lock:
            self._check_sealed()
            if plugin_id not in self._descriptors:
                raise ValueError(f"Plugin ID {plugin_id} not found.")

            self._extensions_by_plugin[plugin_id].extend(extensions)
            # We will gather these by type in get_extensions dynamically

    def transition_state(self, plugin_id: str, new_state: PluginLifecycleState) -> None:
         """Transition the lifecycle state of a plugin."""
         with self._lock:
              self._check_sealed()

              if plugin_id not in self._descriptors:
                   raise ValueError(f"Plugin ID {plugin_id} not found.")

              self._plugin_states[plugin_id] = new_state
              self._diagnostics["lifecycle"][plugin_id] = new_state.value

    def validate_dependencies(self) -> None:
        """Validate dependencies for all registered plugins."""
        with self._lock:
             self._check_sealed()

             for plugin_id, descriptor in self._descriptors.items():
                 # Check required dependencies
                 for req_plugin_id, req_version in descriptor.dependencies.items():
                     if req_plugin_id not in self._descriptors:
                         if plugin_id not in self._diagnostics["dependency"]:
                             self._diagnostics["dependency"][plugin_id] = []
                         if isinstance(self._diagnostics["dependency"][plugin_id], str):
                             self._diagnostics["dependency"][plugin_id] = [self._diagnostics["dependency"][plugin_id]]
                         self._diagnostics["dependency"][plugin_id].append(f"Missing required dependency: {req_plugin_id}")
                         self.transition_state(plugin_id, PluginLifecycleState.FAILED)
                         continue

                     req_descriptor = self._descriptors[req_plugin_id]
                     if not SemanticVersion.is_compatible(req_descriptor.version, req_version):
                         if plugin_id not in self._diagnostics["dependency"]:
                             self._diagnostics["dependency"][plugin_id] = []
                         if isinstance(self._diagnostics["dependency"][plugin_id], str):
                             self._diagnostics["dependency"][plugin_id] = [self._diagnostics["dependency"][plugin_id]]
                         self._diagnostics["dependency"][plugin_id].append(f"Incompatible dependency version: {req_plugin_id} {req_descriptor.version} does not satisfy {req_version}")
                         self.transition_state(plugin_id, PluginLifecycleState.FAILED)

                 # Check optional dependencies
                 for opt_plugin_id, opt_version in descriptor.optional_dependencies.items():
                     if opt_plugin_id not in self._descriptors:
                         if plugin_id not in self._diagnostics["dependency"]:
                             self._diagnostics["dependency"][plugin_id] = []
                         if isinstance(self._diagnostics["dependency"][plugin_id], str):
                             self._diagnostics["dependency"][plugin_id] = [self._diagnostics["dependency"][plugin_id]]
                         self._diagnostics["dependency"][plugin_id].append(f"Missing optional dependency: {opt_plugin_id}")
                     else:
                         opt_descriptor = self._descriptors[opt_plugin_id]
                         if not SemanticVersion.is_compatible(opt_descriptor.version, opt_version):
                             if plugin_id not in self._diagnostics["dependency"]:
                                 self._diagnostics["dependency"][plugin_id] = []
                             if isinstance(self._diagnostics["dependency"][plugin_id], str):
                                 self._diagnostics["dependency"][plugin_id] = [self._diagnostics["dependency"][plugin_id]]
                             self._diagnostics["dependency"][plugin_id].append(f"Incompatible optional dependency version: {opt_plugin_id} {opt_descriptor.version} does not satisfy {opt_version}")

             # Perform topological sort / circular dependency check
             self._check_circular_dependencies()

    def _check_circular_dependencies(self) -> None:
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycle_detected = False

        def dfs(node: str, path: List[str]) -> bool:
            nonlocal cycle_detected
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            descriptor = self._descriptors.get(node)
            if descriptor:
                for neighbor in descriptor.dependencies:
                    if neighbor not in visited:
                        if dfs(neighbor, path):
                            return True
                    elif neighbor in rec_stack:
                        cycle_path = path[path.index(neighbor):] + [neighbor]
                        self._diagnostics["dependency"]["global"] = f"Circular dependency detected: {' -> '.join(cycle_path)}"
                        for n in cycle_path[:-1]:
                            self.transition_state(n, PluginLifecycleState.FAILED)
                        cycle_detected = True
                        return True

            rec_stack.remove(node)
            path.pop()
            return False

        for plugin_id in self._descriptors:
            if plugin_id not in visited:
                if dfs(plugin_id, []):
                    pass

    def get_extensions(self, extension_type: Type[ExtensionPoint]) -> List[ExtensionPoint]:
        """Retrieve all registered extensions of a specific type."""
        with self._lock:
            extensions = []
            for plugin_extensions in self._extensions_by_plugin.values():
                for ext in plugin_extensions:
                    if isinstance(ext, extension_type):
                        extensions.append(ext)
            return extensions

    def get_descriptor(self, plugin_id: str) -> Optional[PluginDescriptor]:
        with self._lock:
             return self._descriptors.get(plugin_id)

    def get_state(self, plugin_id: str) -> Optional[PluginLifecycleState]:
         with self._lock:
              return self._plugin_states.get(plugin_id)


    def get_by_capability(self, capability) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if capability in desc.capabilities]

    def get_by_priority(self, priority) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if desc.priority == priority]

    def get_by_permission(self, permission) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if permission in desc.permissions]

    def get_by_trust_level(self, trust_level) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if desc.trust_level == trust_level]

    def get_by_compiler_stage(self, stage: str) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if stage in desc.required_compiler_stages]

    def get_by_backend_family(self, family: str) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if family in desc.supported_backend_families]

    def get_by_execution_family(self, family: str) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if family in desc.supported_execution_families]

    def get_by_dependency(self, plugin_id: str) -> List[PluginDescriptor]:
        with self._lock:
            return [desc for desc in self._descriptors.values() if plugin_id in desc.dependencies or plugin_id in desc.optional_dependencies]

    def get_by_version_compatibility(self, compiler_version: str, runtime_version: str) -> List[PluginDescriptor]:
        with self._lock:
            compatible = []
            for desc in self._descriptors.values():
                comp_ok = not desc.supported_compiler_versions or compiler_version in desc.supported_compiler_versions
                run_ok = not desc.supported_runtime_versions or runtime_version in desc.supported_runtime_versions
                if comp_ok and run_ok:
                    compatible.append(desc)
            return compatible

    def get_extensions_by_capability(self, capability) -> List[ExtensionPoint]:
        with self._lock:
            extensions = []
            for exts in self._extensions_by_plugin.values():
                for ext in exts:
                    if capability in ext.capabilities:
                        extensions.append(ext)
            return extensions

    def generate_diagnostics_report(self) -> Dict[str, Any]:
        """Return the collected diagnostics report."""
        with self._lock:
            # Populate trust and permission dynamically
            for pid, desc in self._descriptors.items():
                 self._diagnostics["trust"][pid] = desc.trust_level.value
                 self._diagnostics["permission"][pid] = [p.value for p in desc.permissions]
            return self._diagnostics.copy()
