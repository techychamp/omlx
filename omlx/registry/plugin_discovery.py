# SPDX-License-Identifier: Apache-2.0
"""
Plugin discovery for OMLX capability bundles.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .capability_registry import GenerationStrategyRegistry


__all__ = ["discover_plugins"]


logger = logging.getLogger(__name__)


def discover_plugins(registry: GenerationStrategyRegistry) -> None:
    """Discover and register plugins via entry points.
    
    Third parties can add Mamba, RWKV, Hyena, etc. without modifying OMLX.
    """
    try:
        import importlib.metadata
        
        # Look for the omlx.strategies entry point group
        entry_points = importlib.metadata.entry_points()
        
        # Python 3.10+ entry_points() returns a SelectableGroups object
        if hasattr(entry_points, "select"):
            strategy_eps = entry_points.select(group="omlx.strategies")
        else:
            # Fallback for older python / some environments
            strategy_eps = entry_points.get("omlx.strategies", [])
            
        for ep in strategy_eps:
            try:
                # The entry point should point to a function that takes a registry
                # and registers its CapabilityBundles.
                plugin_func = ep.load()
                plugin_func(registry)
                logger.info(f"Loaded OMLX strategy plugin: {ep.name}")
            except Exception as e:
                logger.warning(f"Failed to load OMLX strategy plugin {ep.name}: {e}")
                
    except ImportError:
        # importlib.metadata not available or failed
        pass
