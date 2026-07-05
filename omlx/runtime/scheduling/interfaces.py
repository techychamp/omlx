# SPDX-License-Identifier: Apache-2.0
"""
Interfaces for OMLX Scheduling subsystem.
"""

import abc
from .types import BackendOperationGraph

class GraphScheduler(abc.ABC):
    """
    Analyzes BackendOperationGraph and produces an ExecutionSchedule.
    """
    @abc.abstractmethod
    def build_schedule(self, graph: BackendOperationGraph) -> 'ExecutionSchedule':
        pass
