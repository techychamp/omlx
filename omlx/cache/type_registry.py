# SPDX-License-Identifier: Apache-2.0
"""
Cache type registry for handler lookup.

This module provides a registry for looking up cache type handlers
by cache type enum or class name string.
"""

import logging
from typing import Any, Dict, Optional

from .type_handlers import (
    ArraysCacheHandler,
    CacheListHandler,
    CacheType,
    CacheTypeHandler,
    DefaultCacheHandler,
    KVCacheHandler,
    MiniMaxM3BatchKVCacheHandler,
    MiniMaxM3KVCacheHandler,
    RotatingKVCacheHandler,
    SizedArraysCache,
)

logger = logging.getLogger(__name__)


class CacheTypeRegistry:
    """Registry for cache type handlers.

    Provides lookup of handlers by:
    - CacheType enum value
    - Class name string (e.g., "KVCache", "ArraysCache")

    Usage:
        handler = CacheTypeRegistry.get_handler(CacheType.KVCACHE)
        handler = CacheTypeRegistry.get_handler_by_class_name("RotatingKVCache")
        cache_type = CacheTypeRegistry.detect_cache_type(cache_obj)
    """

    _default_instance: Optional["CacheTypeRegistry"] = None

    def __init__(self) -> None:
        self._handlers: Dict[CacheType, CacheTypeHandler] = {}
        self._class_name_map: Dict[str, CacheType] = {
            "KVCache": CacheType.KVCACHE,
            "RotatingKVCache": CacheType.ROTATING_KVCACHE,
            # omlx subclass that overrides size() to clamp by actual buffer
            # length (defined in omlx/cache/_rotating_subclass.py). Cache
            # restore serializes type(cache).__name__, so the registry must
            # recognize this name to route through RotatingKVCacheHandler;
            # otherwise the default handler reconstructs vanilla
            # RotatingKVCache and the size() override is lost.
            "PrefillReadyRotatingKVCache": CacheType.ROTATING_KVCACHE,
            "BatchKVCache": CacheType.BATCH_KVCACHE,
            "BatchRotatingKVCache": CacheType.BATCH_ROTATING_KVCACHE,
            "ArraysCache": CacheType.ARRAYS_CACHE,
            "QuantizedKVCache": CacheType.QUANTIZED_KVCACHE,
            "CacheList": CacheType.CACHE_LIST,
            # TurboQuant: handled specially in prefix_cache/paged_ssd_cache,
            # mapped to KVCACHE so supports_block_slicing = True (but prefix_cache
            # checks the class name first and routes to TQ-specific handling)
            "TurboQuantKVCache": CacheType.KVCACHE,
            "BatchTurboQuantKVCache": CacheType.KVCACHE,
            # DeepSeek V4 compressed-attention pool. Handlers live in
            # patches/deepseek_v4/cache_handlers.py and register on patch apply.
            "PoolingCache": CacheType.POOLING_CACHE,
            "BatchPoolingCache": CacheType.BATCH_POOLING_CACHE,
            "MiniMaxM3KVCache": CacheType.MINIMAX_M3_KVCACHE,
            "MiniMaxM3BatchKVCache": CacheType.MINIMAX_M3_BATCH_KVCACHE,
        }
        self._default_handler: CacheTypeHandler = DefaultCacheHandler()
        self._initialize_default_handlers()

    def _initialize_default_handlers(self) -> None:
        self._register(KVCacheHandler())
        self._register(RotatingKVCacheHandler())
        self._register(ArraysCacheHandler())
        self._register(CacheListHandler())
        self._register(MiniMaxM3KVCacheHandler())
        self._register(MiniMaxM3BatchKVCacheHandler())

    def _register(self, handler: CacheTypeHandler) -> None:
        self._handlers[handler.cache_type] = handler

    @classmethod
    def _get_active_registry(cls) -> "CacheTypeRegistry":
        from omlx.server import get_runtime
        runtime = get_runtime()
        if runtime and hasattr(runtime, "cache_type_registry") and runtime.cache_type_registry:
            return runtime.cache_type_registry
        if cls._default_instance is None:
            cls._default_instance = cls()
        return cls._default_instance

    @classmethod
    def register(cls, handler: CacheTypeHandler) -> None:
        """Register a handler for a cache type.

        Args:
            handler: Handler instance to register
        """
        cls._get_active_registry()._register(handler)

    @classmethod
    def get_handler(cls, cache_type: CacheType) -> CacheTypeHandler:
        """Get handler for a cache type.

        Args:
            cache_type: The cache type enum

        Returns:
            Handler for the cache type, or default handler if not found
        """
        registry = cls._get_active_registry()
        handler = registry._handlers.get(cache_type)
        if handler is None:
            logger.debug(f"No handler for {cache_type}, using default")
            return registry._default_handler
        return handler

    @classmethod
    def get_handler_by_class_name(cls, class_name: str) -> CacheTypeHandler:
        """Get handler by mlx-lm class name.

        Args:
            class_name: The class name string (e.g., "KVCache")

        Returns:
            Handler for the cache type, or default handler if not found
        """
        registry = cls._get_active_registry()
        # Handle SizedArraysCache wrapper - use ArraysCache handler
        if class_name == "SizedArraysCache":
            return cls.get_handler(CacheType.ARRAYS_CACHE)

        cache_type = registry._class_name_map.get(class_name)
        if cache_type is None:
            logger.debug(f"Unknown cache class '{class_name}', using default handler")
            return registry._default_handler
        return cls.get_handler(cache_type)

    @classmethod
    def is_rotating_family(cls, class_name: str) -> bool:
        """Check whether a class name belongs to the RotatingKVCache family.

        Stored blocks serialize ``type(cache).__name__``, so subclasses such
        as PrefillReadyRotatingKVCache (used for warm-restored caches) appear
        under their live class name. Callers that need "is this a rotating
        layer?" must match the family through this registry rather than
        comparing exact class names.

        Args:
            class_name: The class name string (e.g., "RotatingKVCache")

        Returns:
            True if the name maps to a rotating cache type
        """
        registry = cls._get_active_registry()
        return registry._class_name_map.get(class_name) in (
            CacheType.ROTATING_KVCACHE,
            CacheType.BATCH_ROTATING_KVCACHE,
        )

    @classmethod
    def detect_cache_type(cls, cache_obj: Any) -> CacheType:
        """Detect cache type from object.

        Args:
            cache_obj: An mlx-lm cache object

        Returns:
            Detected CacheType enum value
        """
        registry = cls._get_active_registry()
        # Handle SizedArraysCache wrapper - detect inner cache type
        if isinstance(cache_obj, SizedArraysCache):
            return CacheType.ARRAYS_CACHE

        class_name = type(cache_obj).__name__
        cache_type = registry._class_name_map.get(class_name)

        if cache_type is None:
            # CacheList: has .caches attribute (tuple/list of sub-caches)
            sub_caches = getattr(cache_obj, "caches", None)
            if isinstance(sub_caches, (list, tuple)) and len(sub_caches) > 0:
                return CacheType.CACHE_LIST

            # Try to detect by checking for known attributes
            if hasattr(cache_obj, "max_size") and hasattr(cache_obj, "_idx"):
                return CacheType.ROTATING_KVCACHE
            elif hasattr(cache_obj, "keys") and hasattr(cache_obj, "values"):
                return CacheType.KVCACHE
            elif hasattr(cache_obj, "cache") and isinstance(
                getattr(cache_obj, "cache", None), list
            ):
                return CacheType.ARRAYS_CACHE

            logger.debug(
                f"Could not detect cache type for {class_name}, assuming KVCache"
            )
            return CacheType.KVCACHE

        return cache_type

    @classmethod
    def get_handler_for_object(cls, cache_obj: Any) -> CacheTypeHandler:
        """Get handler for a cache object.

        Convenience method that detects type and returns handler.

        Args:
            cache_obj: An mlx-lm cache object

        Returns:
            Appropriate handler for the object
        """
        cache_type = cls.detect_cache_type(cache_obj)
        return cls.get_handler(cache_type)

    @classmethod
    def is_sliceable(cls, cache_obj: Any) -> bool:
        """Check if a cache object supports block slicing.

        Args:
            cache_obj: An mlx-lm cache object

        Returns:
            True if the cache supports sequence-level slicing
        """
        handler = cls.get_handler_for_object(cache_obj)
        return handler.supports_block_slicing

    @classmethod
    def get_class_name_for_type(cls, cache_type: CacheType) -> str:
        """Get mlx-lm class name for a cache type.

        Args:
            cache_type: CacheType enum

        Returns:
            Class name string
        """
        registry = cls._get_active_registry()
        # Reverse lookup
        for class_name, ct in registry._class_name_map.items():
            if ct == cache_type:
                return class_name
        return cache_type.value

    @classmethod
    def list_registered_types(cls) -> list:
        """List all registered cache types.

        Returns:
            List of registered CacheType enums
        """
        registry = cls._get_active_registry()
        return list(registry._handlers.keys())

    @classmethod
    def list_known_class_names(cls) -> list:
        """List all known mlx-lm class names.

        Returns:
            List of class name strings
        """
        registry = cls._get_active_registry()
        return list(registry._class_name_map.keys())


def _initialize_default_handlers() -> None:
    CacheTypeRegistry._default_instance = CacheTypeRegistry()


# Initialize handlers when module is imported
_initialize_default_handlers()

