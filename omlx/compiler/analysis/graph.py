# SPDX-License-Identifier: Apache-2.0

from typing import Iterator
from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode

class AnalysisGraph:
    """
    Wraps the ExecutionIR and ModelDescriptor to provide standard
    traversal methods for Analysis Passes.
    """

    def __init__(self, descriptor: ModelDescriptor, ir: ExecutionIR):
        self.descriptor = descriptor
        self.ir = ir

    def nodes(self) -> Iterator[IRNode]:
        """Iterate over all nodes in the graph."""
        yield from self.ir.nodes.values()

    def get_node(self, node_id: str) -> IRNode:
        """Fetch a specific node by ID."""
        return self.ir.get_node(node_id)
