# SPDX-License-Identifier: Apache-2.0
"""
Generation metrics for OMLX runtime.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


__all__ = ["GenerationMetrics"]


@dataclass
class GenerationMetrics:
    """Per-request generation statistics. Owned by RuntimeState."""
    tokens_generated: int = 0
    tokens_accepted: int = 0       # spec decoding: accepted draft tokens
    tokens_drafted: int = 0        # spec decoding: total drafted
    tokens_rejected: int = 0       # spec decoding: rejected
    denoising_iterations: int = 0  # diffusion: denoising pass count
    prefill_latency_ms: float = 0.0
    decode_latency_ms: float = 0.0
    peak_memory_bytes: int = 0
    cache_hit_tokens: int = 0
    cache_miss_tokens: int = 0
    _decode_start: float = field(default=0.0, repr=False)

    def start_decode(self) -> None:
        """Mark the start of a decode step."""
        self._decode_start = time.perf_counter()

    def record_decode_step(self) -> None:
        """Record the elapsed time for the current decode step."""
        if self._decode_start > 0:
            self.decode_latency_ms += (time.perf_counter() - self._decode_start) * 1000.0

    @property
    def acceptance_rate(self) -> float:
        """Calculate the speculative decoding acceptance rate."""
        return self.tokens_accepted / max(1, self.tokens_drafted)
