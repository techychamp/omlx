from typing import Dict, List
from .models import FeatureFlag, FlagCategory

class FeatureFlagRegistry:
    def __init__(self):
        self._flags: Dict[str, FeatureFlag] = {}

    def register(self, flag: FeatureFlag):
        if flag.name in self._flags:
            raise ValueError(f"Feature flag {flag.name} already registered")
        self._flags[flag.name] = flag

    def get_flag(self, name: str) -> FeatureFlag:
        if name not in self._flags:
            raise ValueError(f"Unknown feature flag: {name}")
        return self._flags[name]

    def list_flags(self) -> List[FeatureFlag]:
        return list(self._flags.values())

    def get_flags_by_category(self, category: FlagCategory) -> List[FeatureFlag]:
        return [f for f in self._flags.values() if f.category == category]
