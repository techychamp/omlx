from typing import Any, Callable, Dict, Type

class Registry:
    def __init__(self, name: str):
        self.name = name
        self._registry: Dict[str, Any] = {}

    def register(self, name: str, item: Any = None) -> Callable:
        def decorator(obj: Any) -> Any:
            if name in self._registry:
                raise ValueError(f"Cannot register '{name}' in {self.name} registry; it already exists.")
            self._registry[name] = obj
            return obj

        if item is not None:
            return decorator(item)
        return decorator

    def get(self, name: str) -> Any:
        if name not in self._registry:
            raise KeyError(f"'{name}' not found in {self.name} registry.")
        return self._registry[name]

    def has(self, name: str) -> bool:
        return name in self._registry

    def list_all(self) -> Dict[str, Any]:
        return self._registry.copy()

class ArchitectureRegistry(Registry):
    def __init__(self):
        super().__init__("architecture")

class OperatorRegistry(Registry):
    def __init__(self):
        super().__init__("operator")

class ImporterRegistry(Registry):
    def __init__(self):
        super().__init__("importer")

class ProviderRegistry(Registry):
    def __init__(self):
        super().__init__("provider")

class OptimizationRegistry(Registry):
    def __init__(self):
        super().__init__("optimization")

architecture_registry = ArchitectureRegistry()
operator_registry = OperatorRegistry()
importer_registry = ImporterRegistry()
provider_registry = ProviderRegistry()
optimization_registry = OptimizationRegistry()
