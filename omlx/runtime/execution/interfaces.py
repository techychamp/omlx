# SPDX-License-Identifier: Apache-2.0
"""
Interfaces for OMLX Execution Engine.
"""

import abc
from typing import Any, Optional, Union
from .types import ExecutionResult
from .context import ExecutionContext
from .artifacts import BackendOperationGraph
from omlx.runtime.scheduling.artifacts import DependencyGraph

class ExecutionDispatcher(abc.ABC):
    """
    Dispatches graph operations sequentially via BackendAdapters without scheduling.
    """
    @abc.abstractmethod
    def dispatch(self, graph: Any, context: ExecutionContext, execution_order=None, schedule=None) -> ExecutionResult:
        pass

class GraphExecutor(abc.ABC):
    """
    Validates and traverses dependency graphs, invoking ExecutionDispatcher on each node.
    """
    @abc.abstractmethod
    def traverse_and_execute(self, graph: Any, context: ExecutionContext) -> ExecutionResult:
        pass

class ExecutionExecutor(abc.ABC):
    """
    Executes graphs and collects metadata.
    """
    @abc.abstractmethod
    def execute(self, graph: Any, context: ExecutionContext) -> ExecutionResult:
        pass
