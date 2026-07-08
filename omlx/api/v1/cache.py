# SPDX-License-Identifier: Apache-2.0
"""
Cache configuration API.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class CacheConfiguration(BaseModel):
    """Configuration for compiler-native caching."""
    enabled: bool = Field(default=False, description="Whether caching is enabled")
    cache_type: str = Field(default="paged", description="Type of cache (e.g., paged, contiguous)")
    capacity: int = Field(default=1024, description="Capacity of the cache")
    element_size: int = Field(default=8, description="Size of each cache element")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional cache metadata")

class CacheStatisticsResponse(BaseModel):
    """Response containing cache statistics."""
    hits: int
    misses: int
    allocations: int
    evictions: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
