# SPDX-License-Identifier: Apache-2.0
"""
Unified Tooling Framework
Provides a central access point for developer tooling.
"""
from typing import Any
import threading
from .registry import ToolingRegistry
from omlx.tooling.inspector.inspector import CompilerInspector
from omlx.tooling.inspector.runtime_inspector import RuntimeInspector
from omlx.tooling.inspector.execution_inspector import ExecutionInspector
from omlx.tooling.inspector.backend_inspector import BackendInspector
from omlx.tooling.inspector.queue_inspector import QueueInspector
from omlx.tooling.validation.validation_helpers import ValidationHelper
from omlx.tooling.profiling.profiler import DeveloperProfiler
from omlx.tooling.benchmark.benchmark_helpers import BenchmarkHelper
from omlx.tooling.snapshot.snapshot import SnapshotManager


class UnifiedTooling:
    """
    Central framework for developer tooling.
    It delegates to registered inspectors, profilers, etc.
    It must never modify runtime behavior.
    """
    def __init__(self):
        self.registry = ToolingRegistry()

        # Register default inspectors
        self.registry.register_inspector("compiler", CompilerInspector())
        self.registry.register_inspector("runtime", RuntimeInspector())
        self.registry.register_inspector("execution", ExecutionInspector())
        self.registry.register_inspector("backend", BackendInspector())
        self.registry.register_inspector("queue", QueueInspector())

        # Register default tools
        self.registry.register_validator("default", ValidationHelper())
        self.registry.register_profiler("default", DeveloperProfiler())
        self.registry.register_benchmark("default", BenchmarkHelper())

        # Managers
        self.snapshot_manager = SnapshotManager()

    def get_inspector(self, name: str) -> Any:
        return self.registry.get_inspector(name)

    def get_validator(self, name: str) -> Any:
        return self.registry.get_validator(name)

    def get_profiler(self, name: str) -> Any:
        return self.registry.get_profiler(name)

    def get_benchmark(self, name: str) -> Any:
        return self.registry.get_benchmark(name)

# Thread-safe Singleton Management
_unified_tooling_instance = None
_unified_tooling_lock = threading.Lock()

def get_tooling() -> UnifiedTooling:
    """Returns the singleton instance of the tooling framework."""
    global _unified_tooling_instance
    if _unified_tooling_instance is None:
        with _unified_tooling_lock:
            if _unified_tooling_instance is None:
                _unified_tooling_instance = UnifiedTooling()
    return _unified_tooling_instance
