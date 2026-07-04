# SPDX-License-Identifier: Apache-2.0
"""
Lowering engine for converting Logical IR to Physical IR.
"""
from __future__ import annotations
import abc
from typing import List, Dict, Any
from types import MappingProxyType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNodeType
from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.ir.physical.operations import PhysicalOperation, PhysicalOperationType

class LoweringPass(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def apply(self, logical_ir: ExecutionIR, operations: Dict[str, PhysicalOperation], metadata: Dict[str, Any]) -> None:
        """Modifies the operation map in place during the lowering process."""
        pass

class DefaultLoweringPass(LoweringPass):
    """A naive 1:1 mapping pass for initial lowering."""
    @property
    def name(self) -> str:
        return "default_1to1_lowering"

    def apply(self, logical_ir: ExecutionIR, operations: Dict[str, PhysicalOperation], metadata: Dict[str, Any]) -> None:
        for node_id, node in logical_ir.nodes.items():
            op_type = PhysicalOperationType.NOOP
            if node.node_type == IRNodeType.FORWARD:
                op_type = PhysicalOperationType.FORWARD
            elif node.node_type == IRNodeType.SAMPLE:
                op_type = PhysicalOperationType.SAMPLING
            elif node.node_type == IRNodeType.CACHE_READ:
                op_type = PhysicalOperationType.CACHE_LOOKUP
            elif node.node_type == IRNodeType.CACHE_WRITE:
                op_type = PhysicalOperationType.CACHE_UPDATE
            elif node.node_type == IRNodeType.BARRIER:
                op_type = PhysicalOperationType.SYNCHRONIZATION

            operations[node_id] = PhysicalOperation(
                id=node_id,
                operation_type=op_type,
                inputs=tuple(node.metadata.get("inputs", [])),
                outputs=tuple(node.metadata.get("outputs", [])),
                dependencies=node.dependencies,
                metadata=MappingProxyType({"original_logical_node": node.node_type.value})
            )

class LoweringEngine:
    """Transforms Logical ExecutionIR into PhysicalIR."""
    def __init__(self, passes: List[LoweringPass] | None = None):
        self.passes = passes or [DefaultLoweringPass()]

    def lower(self, logical_ir: ExecutionIR) -> PhysicalIR:
        operations: Dict[str, PhysicalOperation] = {}
        metadata: Dict[str, Any] = {"lowered_from": "ExecutionIR"}

        for lowering_pass in self.passes:
            lowering_pass.apply(logical_ir, operations, metadata)

        return PhysicalIR(
            operations=MappingProxyType(operations),
            roots=logical_ir.roots,
            metadata=MappingProxyType(metadata)
        )
