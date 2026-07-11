# SPDX-License-Identifier: Apache-2.0
"""
Generation strategies for OMLX.
"""

from __future__ import annotations

from .autoregressive import AutoregressiveStrategy
from .diffusion import DiffusionStrategy
from .linear_speculation import LinearSpeculationStrategy

__all__ = [
    "AutoregressiveStrategy",
    "DiffusionStrategy",
    "LinearSpeculationStrategy",
]
