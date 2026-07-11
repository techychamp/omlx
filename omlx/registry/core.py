# SPDX-License-Identifier: Apache-2.0
"""
Core implementations of specific registries inheriting from GenericRegistry.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from .base import GenericRegistry, RegistryEntry


@dataclass
class MetadataCapabilityEntry(RegistryEntry):
    pass


class MetadataCapabilityRegistry(GenericRegistry[MetadataCapabilityEntry]):
    pass


@dataclass
class MetadataExecutionModeEntry(RegistryEntry):
    pass


class MetadataExecutionModeRegistry(GenericRegistry[MetadataExecutionModeEntry]):
    pass


@dataclass
class MetadataExecutionProfileEntry(RegistryEntry):
    pass


class MetadataExecutionProfileRegistry(GenericRegistry[MetadataExecutionProfileEntry]):
    pass


@dataclass
class MetadataAdapterEntry(RegistryEntry):
    pass


class MetadataAdapterRegistry(GenericRegistry[MetadataAdapterEntry]):
    pass


@dataclass
class MetadataPluginEntry(RegistryEntry):
    pass


class MetadataPluginRegistry(GenericRegistry[MetadataPluginEntry]):
    pass


@dataclass
class MetadataVerificationEntry(RegistryEntry):
    pass


class MetadataVerificationRegistry(GenericRegistry[MetadataVerificationEntry]):
    pass


@dataclass
class MetadataBackendEntry(RegistryEntry):
    pass


class MetadataBackendRegistry(GenericRegistry[MetadataBackendEntry]):
    pass


class RegistryContainer:
    """Container for all metadata registries, owned by Runtime."""
    def __init__(self) -> None:
        self.capabilities = MetadataCapabilityRegistry()
        self.execution_modes = MetadataExecutionModeRegistry()
        self.execution_profiles = MetadataExecutionProfileRegistry()
        self.adapters = MetadataAdapterRegistry()
        self.plugins = MetadataPluginRegistry()
        self.verifications = MetadataVerificationRegistry()
        self.backends = MetadataBackendRegistry()

    def lock_all(self) -> None:
        """Lock all registered metadata registries to make them immutable."""
        self.capabilities.lock()
        self.execution_modes.lock()
        self.execution_profiles.lock()
        self.adapters.lock()
        self.plugins.lock()
        self.verifications.lock()
        self.backends.lock()

