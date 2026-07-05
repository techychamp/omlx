# SPDX-License-Identifier: Apache-2.0
"""
Tooling Registry
Registers inspectors, profilers, validators, etc.
"""
from typing import Any, Dict, Type

class ToolingRegistry:
    def __init__(self):
        self._inspectors: Dict[str, Any] = {}
        self._validators: Dict[str, Any] = {}
        self._profilers: Dict[str, Any] = {}
        self._benchmarks: Dict[str, Any] = {}

    def register_inspector(self, name: str, inspector: Any):
        self._inspectors[name] = inspector

    def get_inspector(self, name: str) -> Any:
        return self._inspectors.get(name)

    def register_validator(self, name: str, validator: Any):
        self._validators[name] = validator

    def get_validator(self, name: str) -> Any:
        return self._validators.get(name)

    def register_profiler(self, name: str, profiler: Any):
        self._profilers[name] = profiler

    def get_profiler(self, name: str) -> Any:
        return self._profilers.get(name)

    def register_benchmark(self, name: str, benchmark: Any):
        self._benchmarks[name] = benchmark

    def get_benchmark(self, name: str) -> Any:
        return self._benchmarks.get(name)
