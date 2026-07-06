# SPDX-License-Identifier: Apache-2.0
"""
Plugin Integration for Tooling
Allows plugins to register custom tooling extensions.
"""
from typing import Any
from omlx.tooling.framework.unified import get_tooling

class ToolingPluginManager:
    """Manages plugin extensions for the tooling framework."""

    def __init__(self):
        self.tooling = get_tooling()

    def register_custom_inspector(self, name: str, inspector: Any):
        self.tooling.registry.register_inspector(name, inspector)

    def register_custom_validator(self, name: str, validator: Any):
        self.tooling.registry.register_validator(name, validator)

    def register_custom_profiler(self, name: str, profiler: Any):
        self.tooling.registry.register_profiler(name, profiler)

    def register_custom_benchmark(self, name: str, benchmark: Any):
        self.tooling.registry.register_benchmark(name, benchmark)
