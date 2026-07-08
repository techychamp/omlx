# SPDX-License-Identifier: Apache-2.0
"""
Tooling Registry
Registers inspectors, profilers, validators, etc., using thread-safe descriptors.
"""
from typing import Any, Dict
import threading
from dataclasses import dataclass, field

@dataclass(frozen=True)
class ToolDescriptor:
    name: str
    tool_type: str
    description: str = ""

@dataclass(frozen=True)
class ToolExtension:
    descriptor: ToolDescriptor
    instance: Any

class ToolingRegistry:
    def __init__(self):
        self._lock = threading.RLock()
        self._inspectors: Dict[str, ToolExtension] = {}
        self._validators: Dict[str, ToolExtension] = {}
        self._profilers: Dict[str, ToolExtension] = {}
        self._benchmarks: Dict[str, ToolExtension] = {}

    def register_inspector(self, name: str, inspector: Any):
        with self._lock:
            descriptor = ToolDescriptor(name=name, tool_type="inspector")
            self._inspectors[name] = ToolExtension(descriptor=descriptor, instance=inspector)

    def get_inspector(self, name: str) -> Any:
        with self._lock:
            extension = self._inspectors.get(name)
            return extension.instance if extension else None

    def register_validator(self, name: str, validator: Any):
        with self._lock:
            descriptor = ToolDescriptor(name=name, tool_type="validator")
            self._validators[name] = ToolExtension(descriptor=descriptor, instance=validator)

    def get_validator(self, name: str) -> Any:
        with self._lock:
            extension = self._validators.get(name)
            return extension.instance if extension else None

    def register_profiler(self, name: str, profiler: Any):
        with self._lock:
            descriptor = ToolDescriptor(name=name, tool_type="profiler")
            self._profilers[name] = ToolExtension(descriptor=descriptor, instance=profiler)

    def get_profiler(self, name: str) -> Any:
        with self._lock:
            extension = self._profilers.get(name)
            return extension.instance if extension else None

    def register_benchmark(self, name: str, benchmark: Any):
        with self._lock:
            descriptor = ToolDescriptor(name=name, tool_type="benchmark")
            self._benchmarks[name] = ToolExtension(descriptor=descriptor, instance=benchmark)

    def get_benchmark(self, name: str) -> Any:
        with self._lock:
            extension = self._benchmarks.get(name)
            return extension.instance if extension else None
