from typing import Dict, Any, Optional, List
from .models import FeatureFlag, FlagCategory
from .registry import FeatureFlagRegistry
from .resolver import FeatureFlagResolver

class ImmutableSnapshot:
    def __init__(self, values: Dict[str, Any], registry: FeatureFlagRegistry):
        self._values = values
        self._registry = registry

    def is_enabled(self, name: str) -> bool:
        flag = self._registry.get_flag(name)
        val = self._values[name]
        return bool(val)

    def get(self, name: str) -> Any:
        self._registry.get_flag(name) # validates existence
        return self._values[name]

    def export(self) -> Dict[str, Any]:
        return dict(self._values)

    def list(self) -> List[FeatureFlag]:
         return self._registry.list_flags()

    def get_flags_by_category(self, category: FlagCategory) -> List[FeatureFlag]:
         return self._registry.get_flags_by_category(category)


class FeatureFlagSystem:
    def __init__(self):
        self._registry = FeatureFlagRegistry()
        self._snapshot: Optional[ImmutableSnapshot] = None
        self._config_overrides: Dict[str, Any] = {}
        self._cli_overrides: Dict[str, Any] = {}

    def register(self, flag: FeatureFlag):
        if self._snapshot is not None:
             raise RuntimeError("Cannot register feature flags after snapshot has been taken")
        self._registry.register(flag)

    def set_config_overrides(self, overrides: Dict[str, Any]):
        if self._snapshot is not None:
            raise RuntimeError("Cannot set overrides after snapshot has been taken")
        self._config_overrides = overrides

    def set_cli_overrides(self, overrides: Dict[str, Any]):
        if self._snapshot is not None:
             raise RuntimeError("Cannot set overrides after snapshot has been taken")
        self._cli_overrides = overrides

    def take_snapshot(self) -> ImmutableSnapshot:
        if self._snapshot is not None:
             return self._snapshot

        resolver = FeatureFlagResolver(self._registry, self._config_overrides, self._cli_overrides)
        values = {}
        for flag in self._registry.list_flags():
            values[flag.name] = resolver.resolve(flag.name)

        self._snapshot = ImmutableSnapshot(values, self._registry)
        return self._snapshot

    @property
    def is_initialized(self):
        return self._snapshot is not None

    def snapshot(self) -> ImmutableSnapshot:
         if self._snapshot is None:
              raise RuntimeError("FeatureFlagSystem snapshot not taken yet. Boot sequence incomplete.")
         return self._snapshot

# Global instance for registration phase, becomes immutable on snapshot
feature_flags_system = FeatureFlagSystem()
