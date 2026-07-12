# SPDX-License-Identifier: Apache-2.0

from typing import Any, Dict
from abc import ABC, abstractmethod
from ..graph import AnalysisGraph

class AnalysisPass(ABC):
    """
    Base interface for all Analysis Passes.
    Passes must be stateless and pure.
    """

    @abstractmethod
    def run(self, graph: AnalysisGraph) -> Dict[str, Any]:
        """
        Executes the pass over the AnalysisGraph and returns extracted features/constraints.
        """
        pass
