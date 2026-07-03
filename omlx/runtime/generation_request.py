# SPDX-License-Identifier: Apache-2.0
"""
Inference-layer wrapper for requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from omlx.request import Request
    from .context import GenerationContext, RuntimeState


__all__ = ["GenerationRequest"]


@dataclass
class GenerationRequest:
    """Inference-layer view of a request.
    
    Wraps the transport-layer Request and adds inference-specific state.
    The scheduler works with GenerationRequest; the API layer works with Request.
    """
    request: Request
    context: GenerationContext | None = None
    state: RuntimeState | None = None

    @property
    def request_id(self) -> str:
        return self.request.request_id

    @property
    def prompt_token_ids(self) -> list[int] | None:
        return self.request.prompt_token_ids

    @property
    def sampling_params(self):
        return self.request.sampling_params
