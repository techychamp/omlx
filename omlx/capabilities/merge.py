from dataclasses import dataclass, field
from typing import Any
from .sources import CapabilitySource
import logging

logger = logging.getLogger("omlx.capabilities.merge")

@dataclass
class CapabilityProvenance:
    value: Any
    winner: str
    history: list[str]

@dataclass
class MergeResult:
    merged_values: dict[str, Any]
    diagnostics: dict[str, CapabilityProvenance]

def merge_sources(sources: list[CapabilitySource], context: Any = None) -> MergeResult:
    """
    Merge capabilities from multiple sources and track provenance.
    Order of sources list implies precedence (earlier overrides later).
    However, the typical usage is passing sources in reverse-precedence order
    and doing a dict update, so the last one wins.
    """
    merged: dict[str, Any] = {}
    diagnostics: dict[str, CapabilityProvenance] = {}

    for source in sources:
        try:
            source_caps = source.get_capabilities(context)
            if source_caps:
                logger.debug(f"Merging capabilities from {source.name}: {source_caps}")
                for key, val in source_caps.items():
                    merged[key] = val
                    if key not in diagnostics:
                        diagnostics[key] = CapabilityProvenance(value=val, winner=source.name, history=[source.name])
                    else:
                        diagnostics[key].value = val
                        diagnostics[key].winner = source.name
                        diagnostics[key].history.append(source.name)
        except Exception as e:
            logger.error(f"Error extracting capabilities from {source.name}: {e}")
            raise

    return MergeResult(merged_values=merged, diagnostics=diagnostics)
