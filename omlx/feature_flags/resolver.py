import os
from typing import Dict, Any, Optional
from .models import FeatureFlag, FlagType

class FeatureFlagResolver:
    def __init__(self, registry, config_overrides: Optional[Dict[str, Any]] = None, cli_overrides: Optional[Dict[str, Any]] = None):
        self._registry = registry
        self._config_overrides = config_overrides or {}
        self._cli_overrides = cli_overrides or {}

    def _parse_env_var(self, env_var_name: str, flag_type: FlagType) -> Optional[Any]:
        val = os.environ.get(env_var_name)
        if val is None:
            return None

        if flag_type == FlagType.BOOLEAN:
            return val.lower() in ("1", "true", "yes", "on")
        elif flag_type == FlagType.INTEGER:
            try:
                return int(val)
            except ValueError:
                return None
        elif flag_type == FlagType.FLOAT:
            try:
                return float(val)
            except ValueError:
                return None
        else:
            return val

    def resolve(self, flag_name: str) -> Any:
        flag = self._registry.get_flag(flag_name)

        # 1. CLI Overrides
        if flag_name in self._cli_overrides:
            return self._cli_overrides[flag_name]

        # 2. Environment Variables
        env_var_name = flag.env_var_name or f"OMLX_FF_{flag_name.upper().replace('-', '_')}"
        env_val = self._parse_env_var(env_var_name, flag.flag_type)
        if env_val is not None:
            return env_val

        # 3. Config Overrides
        if flag_name in self._config_overrides:
            return self._config_overrides[flag_name]

        # 4. Default Value
        return flag.default_value
