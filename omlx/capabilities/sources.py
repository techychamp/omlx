from abc import ABC, abstractmethod
from typing import Any

from .descriptor import ExecutionFamily, AttentionType, CacheLayoutType

class CapabilitySource(ABC):
    @abstractmethod
    def get_capabilities(self, context: Any) -> dict[str, Any]:
        """Return a dictionary of capabilities."""
        pass

    @property
    @abstractmethod
    def source_id(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        """Name of the source for diagnostics."""
        pass

class ModelMetadataSource(CapabilitySource):
    def __init__(self, raw_config: dict[str, Any]):
        self.raw_config = raw_config

    @property
    def source_id(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return "ModelMetadataSource"

    def get_capabilities(self, context: Any = None) -> dict[str, Any]:
        caps: dict[str, Any] = {}
        model_type = self.raw_config.get("model_type", "").lower()

        if "diffusion" in model_type:
            caps["execution_family"] = ExecutionFamily.DIFFUSION
            caps["attention_types"] = [AttentionType.DIFFUSION]
            caps["cache_layout"] = CacheLayoutType.NONE
            caps["supports_diffusion"] = True
            caps["supports_streaming"] = False
        elif "embedding" in model_type:
            caps["execution_family"] = ExecutionFamily.EMBEDDING
            caps["attention_types"] = [AttentionType.BIDIRECTIONAL]
            caps["cache_layout"] = CacheLayoutType.NONE
            caps["supports_embedding"] = True
            caps["supports_streaming"] = False
        else:
            caps["execution_family"] = ExecutionFamily.AUTOREGRESSIVE

        return caps

class FeatureFlagSource(CapabilitySource):
    def __init__(self, flags_system: Any):
        self.flags_system = flags_system

    @property
    def source_id(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return "FeatureFlagSource"

    def get_capabilities(self, context: Any = None) -> dict[str, Any]:
        caps: dict[str, Any] = {}
        # In a real implementation, this would query the ImmutableSnapshot of FeatureFlags
        # for relevant capability overrides (e.g. force speculative decoding)
        return caps

class RuntimeOverrideSource(CapabilitySource):
    def __init__(self, overrides: dict[str, Any]):
        self.overrides = overrides

    @property
    def source_id(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return "RuntimeOverrideSource"

    def get_capabilities(self, context: Any = None) -> dict[str, Any]:
        return self.overrides.copy()

class PluginSource(CapabilitySource):
    def __init__(self, plugins: list[Any]):
        self.plugins = plugins

    @property
    def source_id(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return "PluginSource"

    def get_capabilities(self, context: Any = None) -> dict[str, Any]:
        caps: dict[str, Any] = {}
        # Iterate over plugins and accumulate capabilities
        return caps
