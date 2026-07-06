# SPDX-License-Identifier: Apache-2.0
"""
Plugin Integration for Model Intelligence.
"""
from typing import List, Protocol

class ArchitectureDetectorPlugin(Protocol):
    def detect_architecture(self, config: dict) -> str:
        ...

class CapabilityAnalyzerPlugin(Protocol):
    def analyze_capabilities(self, config: dict, arch: str, family: str) -> dict:
        ...

class MetadataParserPlugin(Protocol):
    def parse_metadata(self, raw_metadata: dict) -> dict:
        ...

class ModelIntelligencePluginManager:
    """
    Manages plugins that contribute to model intelligence.
    """
    def __init__(self):
        self._architecture_detectors: List[ArchitectureDetectorPlugin] = []
        self._capability_analyzers: List[CapabilityAnalyzerPlugin] = []
        self._metadata_parsers: List[MetadataParserPlugin] = []

    def register_architecture_detector(self, plugin: ArchitectureDetectorPlugin) -> None:
        self._architecture_detectors.append(plugin)

    def register_capability_analyzer(self, plugin: CapabilityAnalyzerPlugin) -> None:
        self._capability_analyzers.append(plugin)

    def register_metadata_parser(self, plugin: MetadataParserPlugin) -> None:
        self._metadata_parsers.append(plugin)

    @property
    def architecture_detectors(self) -> List[ArchitectureDetectorPlugin]:
        return self._architecture_detectors

    @property
    def capability_analyzers(self) -> List[CapabilityAnalyzerPlugin]:
        return self._capability_analyzers

    @property
    def metadata_parsers(self) -> List[MetadataParserPlugin]:
        return self._metadata_parsers

# Global plugin manager for the framework
_plugin_manager = ModelIntelligencePluginManager()

def get_plugin_manager() -> ModelIntelligencePluginManager:
    return _plugin_manager
