# SPDX-License-Identifier: Apache-2.0
"""
Adapter Registry.
"""
from __future__ import annotations
import threading
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass, field
from .adapter import BaseBackendAdapter
from .selection.lifecycle import BackendLifecycleState

@dataclass(frozen=True)
class AdapterRegistration:
    backend: str
    hardware: str
    execution_family: str
    execution_mode: str
    # NOTE: The adapter is assumed to be strictly stateless and thread-safe.
    # While the instance reference is frozen here, we trust it complies with oMLX architecture.
    adapter: BaseBackendAdapter
    version: str = "1.0.0"
    priority: int = 0
    lifecycle_state: BackendLifecycleState = BackendLifecycleState.REGISTERED
    is_plugin: bool = False
    aliases: Tuple[str, ...] = field(default_factory=tuple)

class AdapterRegistry:
    """Registry to resolve hardware/software adapters based on execution target details."""
    
    def __init__(self) -> None:
        # Key: (backend, hardware, execution_family, execution_mode) -> list of registrations
        self._adapters: Dict[Tuple[str, str, str, str], List[AdapterRegistration]] = {}
        self._is_locked = False
        self._lock = threading.RLock()

    def register(
        self,
        backend: str,
        hardware: str,
        execution_family: str,
        execution_mode: str,
        adapter: BaseBackendAdapter,
        version: str = "1.0.0",
        priority: int = 0,
        lifecycle_state: BackendLifecycleState | str = BackendLifecycleState.REGISTERED,
        is_plugin: bool = False,
        aliases: Tuple[str, ...] = tuple()
    ) -> None:
        with self._lock:
            if self._is_locked:
                raise RuntimeError("AdapterRegistry is locked and cannot be modified.")

            if isinstance(lifecycle_state, str):
                lifecycle_state = BackendLifecycleState(lifecycle_state.upper())

            key = (backend.lower(), hardware.lower(), execution_family.lower(), execution_mode.lower())

            registration = AdapterRegistration(
                backend=backend.lower(),
                hardware=hardware.lower(),
                execution_family=execution_family.lower(),
                execution_mode=execution_mode.lower(),
                adapter=adapter,
                version=version,
                priority=priority,
                lifecycle_state=lifecycle_state,
                is_plugin=is_plugin,
                aliases=aliases
            )

            if key not in self._adapters:
                self._adapters[key] = []

            # Allow multiple adapters for the same key.
            self._adapters[key].append(registration)
            self._adapters[key].sort(key=lambda r: r.priority, reverse=True)

    def resolve(self, backend: str, hardware: str, execution_family: str, execution_mode: str) -> BaseBackendAdapter:
        with self._lock:
            key = (backend.lower(), hardware.lower(), execution_family.lower(), execution_mode.lower())
            registrations = self._adapters.get(key)
            if not registrations:
                raise ValueError(
                    f"No adapter registered for target: backend={backend}, hardware={hardware}, "
                    f"execution_family={execution_family}, execution_mode={execution_mode}"
                )

            for reg in registrations:
                if reg.lifecycle_state not in (BackendLifecycleState.UNAVAILABLE, BackendLifecycleState.DISABLED):
                    return reg.adapter

            # Fallback to the first one if all are unavailable/disabled
            return registrations[0].adapter

    def exists(self, backend: str, hardware: str, execution_family: str, execution_mode: str) -> bool:
        with self._lock:
            key = (backend.lower(), hardware.lower(), execution_family.lower(), execution_mode.lower())
            return key in self._adapters and len(self._adapters[key]) > 0

    def query(self, **kwargs) -> List[AdapterRegistration]:
        """
        Query adapters by metadata.
        """
        with self._lock:
            results = []
            for regs in self._adapters.values():
                for reg in regs:
                    match = True
                    for k, v in kwargs.items():
                        if k == "lifecycle_state" and isinstance(v, str):
                            v = BackendLifecycleState(v.upper())

                        if not hasattr(reg, k) or getattr(reg, k) != v:
                            match = False
                            break

                    if match:
                        results.append(reg)
            return results

    def lock(self) -> None:
        with self._lock:
            self._is_locked = True
