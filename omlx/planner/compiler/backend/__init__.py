# SPDX-License-Identifier: Apache-2.0
"""
Backend Adapter Framework & Compiler Backend.
"""
from .descriptor import BackendCapability, BackendDescriptor, BackendDescriptorRegistry
from .operations import (
    BackendOperation,
    BackendOperationGraph,
    ReferenceBackendOperation,
    MLXOperation,
    MLXForwardOperation,
    MLXSamplingOperation,
    MLXCacheLookupOperation,
    MLXCacheUpdateOperation,
    MLXSynchronizationOperation,
    MLXNoOpOperation,
)
from .adapter import (
    BackendValidationResult,
    TranslationResult,
    BaseBackendAdapter,
    MLXAdapter,
)
from .registry import AdapterRegistry

__all__ = [
    "BackendCapability",
    "BackendDescriptor",
    "BackendDescriptorRegistry",
    "BackendOperation",
    "BackendOperationGraph",
    "ReferenceBackendOperation",
    "MLXOperation",
    "MLXForwardOperation",
    "MLXSamplingOperation",
    "MLXCacheLookupOperation",
    "MLXCacheUpdateOperation",
    "MLXSynchronizationOperation",
    "MLXNoOpOperation",
    "BackendValidationResult",
    "TranslationResult",
    "BaseBackendAdapter",
    "MLXAdapter",
    "AdapterRegistry",
]
