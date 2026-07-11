# SPDX-License-Identifier: Apache-2.0
"""
Generation modes for OMLX inference.
"""

from __future__ import annotations

import enum


__all__ = ["GenerationMode"]


class GenerationMode(enum.Enum):
    """Supported generation modes in OMLX."""
    AUTOREGRESSIVE = "autoregressive"
    DIFFUSION = "diffusion"
    LINEAR_SPECULATION = "linear_speculation"
