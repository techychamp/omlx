# SPDX-License-Identifier: Apache-2.0
"""
Inference components for OMLX tri-mode generation.
"""

from __future__ import annotations

from .attention import AttentionDescriptor, AttentionMode
from .cache_policy import CachePolicy, DefaultCachePolicy
from .execution_graph import (
    ExecutionGraph,
    GraphNode,
    GraphNodeType,
    build_autoregressive_graph,
    build_diffusion_graph,
    build_linear_speculation_graph,
)
from .modes import GenerationMode
from .sampler_interface import SamplerInterface, SamplerParams, make_sampler_interface
from .strategies.autoregressive import AutoregressiveStrategy
from .strategies.diffusion import DiffusionStrategy
from .strategies.linear_speculation import LinearSpeculationStrategy
from .strategy import BaseGenerationStrategy
from .strategy_types import ForwardResult, PostprocessResult, PrefillResult
from .streaming import StreamingDelta


__all__ = [
    "AttentionDescriptor",
    "AttentionMode",
    "AutoregressiveStrategy",
    "BaseGenerationStrategy",
    "CachePolicy",
    "DefaultCachePolicy",
    "DiffusionStrategy",
    "ExecutionGraph",
    "ForwardResult",
    "GenerationMode",
    "GraphNode",
    "GraphNodeType",
    "LinearSpeculationStrategy",
    "PostprocessResult",
    "PrefillResult",
    "SamplerInterface",
    "SamplerParams",
    "StreamingDelta",
    "build_autoregressive_graph",
    "build_diffusion_graph",
    "build_linear_speculation_graph",
    "make_sampler_interface",
]
