# SPDX-License-Identifier: Apache-2.0
"""
Generic registry infrastructure for OMLX.

Provides the foundational classes for metadata registries:
- RegistryPhase: Enums for registry lifecycle.
- RegistryEntry: Base model for registry items.
- GenericRegistry: The core registry implementation.
"""

from __future__ import annotations

import copy
import enum
import json
import threading
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generic, Iterator, List, Optional, Set, TypeVar

class RegistryPhase(enum.Enum):
    UNINITIALIZED = "uninitialized"
    BUILDING = "building"
    LOCKED = "locked"
    SHUTDOWN = "shutdown"

class RegistryLockedError(Exception):
    pass

class RegistryDuplicateError(Exception):
    pass

class RegistryDependencyError(Exception):
    pass

@dataclass
class RegistryEntry:
    id: str
    display_name: str
    description: str
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "system"
    source: str = "internal"
    status: str = "active"
    deprecation_metadata: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegistryEntry":
        # Create a copy so we can pop
        d = copy.deepcopy(data)
        return cls(**d)

T = TypeVar("T", bound=RegistryEntry)

class GenericRegistry(Generic[T]):
    def __init__(self) -> None:
        self._entries: Dict[str, T] = {}
        self._aliases: Dict[str, str] = {}  # alias -> entry_id
        self._phase = RegistryPhase.UNINITIALIZED
        self._lock = threading.RLock()

        # Start building immediately upon instantiation
        self.transition_to(RegistryPhase.BUILDING)

    def transition_to(self, phase: RegistryPhase) -> None:
        with self._lock:
            if phase == RegistryPhase.LOCKED:
                self._validate_dependencies()
            self._phase = phase

    def register(self, entry: T) -> None:
        with self._lock:
            if self._phase != RegistryPhase.BUILDING:
                raise RegistryLockedError(f"Cannot register {entry.id}: Registry is {self._phase.value}")

            if entry.id in self._entries:
                raise RegistryDuplicateError(f"Entry ID {entry.id} already exists.")

            for alias in entry.aliases:
                if alias in self._aliases or alias in self._entries:
                    raise RegistryDuplicateError(f"Alias {alias} already exists.")

            # Store the entry
            self._entries[entry.id] = entry

            # Store aliases
            for alias in entry.aliases:
                self._aliases[alias] = entry.id

    def lock(self) -> None:
        """Lock the registry, making it immutable and validating dependencies."""
        self.transition_to(RegistryPhase.LOCKED)

    def shutdown(self) -> None:
        """Transition to shutdown phase."""
        self.transition_to(RegistryPhase.SHUTDOWN)

    def get(self, identifier: str) -> Optional[T]:
        """Get an entry by ID or alias. Thread-safe."""
        with self._lock:
            if identifier in self._entries:
                return self._entries[identifier]
            if identifier in self._aliases:
                return self._entries[self._aliases[identifier]]
            return None

    def exists(self, identifier: str) -> bool:
        """Check if an entry exists by ID or alias."""
        return self.get(identifier) is not None

    def __iter__(self) -> Iterator[T]:
        with self._lock:
            # Yield from a shallow copy to prevent modification during iteration
            return iter(list(self._entries.values()))

    def _validate_dependencies(self) -> None:
        """Validates that all dependencies exist and there are no cycles."""
        visited: Set[str] = set()
        path: Set[str] = set()

        def visit(entry_id: str) -> None:
            if entry_id in path:
                raise RegistryDependencyError(f"Dependency cycle detected involving: {entry_id}")
            if entry_id in visited:
                return

            if entry_id not in self._entries:
                # Dependency refers to something not in registry
                # For some registries this might be fine if referring to external things,
                # but we validate strict existence within the same registry for simplicity,
                # or just log a warning. Let's raise an error.
                raise RegistryDependencyError(f"Missing dependency: {entry_id}")

            path.add(entry_id)
            for dep in self._entries[entry_id].dependencies:
                visit(dep)
            path.remove(entry_id)
            visited.add(entry_id)

        for entry_id in self._entries:
            visit(entry_id)

    def to_json(self) -> str:
        """Serialize registry entries to JSON."""
        with self._lock:
            entries_dict = {
                entry_id: entry.to_dict()
                for entry_id, entry in self._entries.items()
            }
            return json.dumps(entries_dict)

    def from_json(self, json_str: str, entry_class: type[T]) -> None:
        """Load entries from JSON. Must be in BUILDING phase."""
        with self._lock:
            if self._phase != RegistryPhase.BUILDING:
                raise RegistryLockedError("Cannot load from JSON: Registry is not building")

            data = json.loads(json_str)
            for item_data in data.values():
                entry = entry_class.from_dict(item_data)
                self.register(entry)
