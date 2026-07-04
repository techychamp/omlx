from typing import Any
from .sources import CapabilitySource
import logging

logger = logging.getLogger("omlx.capabilities.merge")

def merge_sources(sources: list[CapabilitySource], context: Any = None) -> dict[str, Any]:
    """
    Merge capabilities from multiple sources.
    Order of sources list implies precedence (earlier overrides later).
    However, the typical usage is passing sources in reverse-precedence order
    and doing a dict update, so the last one wins.

    Standard precedence (lowest to highest priority):
    1. Defaults (implicit in the Descriptor initialization)
    2. Model metadata
    3. Adapter metadata
    4. Plugins
    5. Feature Flags
    6. Runtime overrides
    """

    merged: dict[str, Any] = {}

    for source in sources:
        try:
            source_caps = source.get_capabilities(context)
            if source_caps:
                logger.debug(f"Merging capabilities from {source.name}: {source_caps}")
                merged.update(source_caps)
        except Exception as e:
            logger.error(f"Error extracting capabilities from {source.name}: {e}")
            raise

    return merged
