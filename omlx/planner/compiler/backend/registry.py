# SPDX-License-Identifier: Apache-2.0
"""
Adapter Registry.
"""
from __future__ import annotations
import threading
from typing import Dict, Tuple
from .adapter import BaseBackendAdapter

class AdapterRegistry:
    """Registry to resolve hardware/software adapters based on execution target details."""
    
    def __init__(self) -> None:
        # Key: (backend, hardware, execution_family, execution_mode)
        self._adapters: Dict[Tuple[str, str, str, str], BaseBackendAdapter] = {}
        self._is_locked = False
        self._lock = threading.RLock()

    def register(self, backend: str, hardware: str, execution_family: str, execution_mode: str, adapter: BaseBackendAdapter) -> None:
        with self._lock:
            if self._is_locked:
                raise RuntimeError("AdapterRegistry is locked and cannot be modified.")
            key = (backend.lower(), hardware.lower(), execution_family.lower(), execution_mode.lower())
            if key in self._adapters:
                raise ValueError(f"Adapter already registered for target: {key}")
            self._adapters[key] = adapter

    def resolve(self, backend: str, hardware: str, execution_family: str, execution_mode: str) -> BaseBackendAdapter:
        with self._lock:
            key = (backend.lower(), hardware.lower(), execution_family.lower(), execution_mode.lower())
            adapter = self._adapters.get(key)
            if adapter is None:
                raise ValueError(
                    f"No adapter registered for target: backend={backend}, hardware={hardware}, "
                    f"execution_family={execution_family}, execution_mode={execution_mode}"
                )
            return adapter

    def exists(self, backend: str, hardware: str, execution_family: str, execution_mode: str) -> bool:
        with self._lock:
            key = (backend.lower(), hardware.lower(), execution_family.lower(), execution_mode.lower())
            return key in self._adapters

    def lock(self) -> None:
        with self._lock:
            self._is_locked = True
