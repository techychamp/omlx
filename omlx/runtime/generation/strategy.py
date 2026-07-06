# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional, Protocol, runtime_checkable

@runtime_checkable
class GenerationStrategy(Protocol):
    """
    Interface for Generation Strategies.
    """

    def generate(self, runtime: Any, request_context: Any, **kwargs) -> Any:
        """
        Orchestrates generation according to the specific strategy.
        """
        ...
