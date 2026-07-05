# SPDX-License-Identifier: Apache-2.0
"""
Interfaces for OMLX Execution Engine.
"""

import abc
from typing import Any, Optional
from .types import ExecutionResult
from .context import ExecutionContext
from .artifacts import BackendOperationGraph

class ExecutionDispatcher(abc.ABC):
    """
    Dispatches graph operations sequentially via BackendAdapters without scheduling.
    """
    @abc.abstractmethod
    def dispatch(self, graph: BackendOperationGraph, context: ExecutionContext, execution_order=None) -> ExecutionResult:
        pass

class GraphExecutor(abc.ABC):
    """
    Validates and traverses BackendOperationGraph, invoking ExecutionDispatcher on each node.
    """
    @abc.abstractmethod
    def traverse_and_execute(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:
        pass

class ExecutionExecutor(abc.ABC):
    """
    Executes BackendOperationGraph and collects metadata.
    """
    @abc.abstractmethod
    def execute(self, graph: BackendOperationGraph, context: ExecutionContext) -> ExecutionResult:
        pass
