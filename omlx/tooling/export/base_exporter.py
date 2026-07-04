# SPDX-License-Identifier: Apache-2.0
from abc import ABC, abstractmethod
from typing import Any

class BaseExporter(ABC):
    """Base class for all graph/compiler artifact exporters."""

    @abstractmethod
    def export(self, data: dict[str, Any], **kwargs) -> str:
        """Exports the given dict data to a string representation."""
        pass
