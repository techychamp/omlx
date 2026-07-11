# SPDX-License-Identifier: Apache-2.0
"""
Interfaces for OMLX Scheduling subsystem.
"""

import abc
from typing import Union
from .types import BackendOperationGraph
from .artifacts import DependencyGraph

class GraphScheduler(abc.ABC):
    """
    Analyzes BackendOperationGraph or DependencyGraph and produces an ExecutionSchedule.
    """
    @abc.abstractmethod
    def build_schedule(self, graph: Union[BackendOperationGraph, DependencyGraph]) -> 'ExecutionSchedule':
        pass
