# SPDX-License-Identifier: Apache-2.0
"""
Backend Adapter interface and implementations.
"""
from __future__ import annotations
import abc
import time
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.ir.physical.operations import PhysicalOperationType
from .descriptor import BackendDescriptor, BackendCapability
from .operations import (
    BackendOperationGraph,
    MLXForwardOperation,
    MLXSamplingOperation,
    MLXCacheLookupOperation,
    MLXCacheUpdateOperation,
    MLXSynchronizationOperation,
    MLXNoOpOperation,
)

@dataclass(frozen=True)
class BackendValidationResult:
    """Rich validation results returned by adapters."""
    is_valid: bool
    unsupported_operations: tuple[str, ...] = tuple()
    unsupported_capabilities: tuple[str, ...] = tuple()
    warnings: tuple[str, ...] = tuple()
    estimated_fallbacks: MappingProxyType[str, str] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: tuple[str, ...] = tuple()

@dataclass(frozen=True)
class TranslationResult:
    """Rich compilation results returned by backend translation."""
    backend_graph: BackendOperationGraph
    warnings: tuple[str, ...] = tuple()
    diagnostics: tuple[str, ...] = tuple()
    statistics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    backend_descriptor: BackendDescriptor = field(default=None)

class BaseBackendAdapter(abc.ABC):
    """Abstract base class for all hardware/software backend adapters."""

    @property
    @abc.abstractmethod
    def descriptor(self) -> BackendDescriptor:
        """Get the immutable descriptor for this backend."""
        pass

    @abc.abstractmethod
    def validate(self, physical_ir: PhysicalIR) -> BackendValidationResult:
        """Validate whether the Physical IR is compatible with this backend."""
        pass

    @abc.abstractmethod
    def translate(self, physical_ir: PhysicalIR) -> TranslationResult:
        """Translate the Physical IR into a backend-native operation graph."""
        pass

    @abc.abstractmethod
    def supports_capability(self, capability: str | BackendCapability) -> bool:
        """Check if the backend supports a specific execution capability."""
        pass

class MLXAdapter(BaseBackendAdapter):
    """Reference implementation of a backend adapter for MLX."""

    def __init__(self) -> None:
        # Resolve version safely
        mlx_version = "unknown"
        try:
            import mlx.core as mx
            mlx_version = mx.__version__
        except ImportError:
            pass

        self._descriptor = BackendDescriptor(
            backend_id="mlx",
            backend_version=mlx_version,
            supported_execution_semantics=("forward", "sampling", "cache_lookup", "cache_update", "synchronization", "noop"),
            supported_operation_mappings=("mlx_forward", "mlx_sampling", "mlx_cache_lookup", "mlx_cache_update", "mlx_synchronization", "mlx_noop"),
            supported_execution_families=("autoregressive", "diffusion", "embedding"),
            supported_cache_layouts=("paged", "flat", "none"),
            supported_synchronization_primitives=("metal_synchronize",),
            supported_optimization_capabilities=("graph_compilation", "unified_memory"),
            hardware_capabilities=("unified_memory", "apple_silicon"),
            memory_model="unified",
            execution_topology="single_node",
            backend_metadata=MappingProxyType({"framework": "mlx", "device": "gpu"})
        )

        self._capabilities = {
            BackendCapability.SPECULATIVE_DECODING,
            BackendCapability.DIFFUSION,
            BackendCapability.VERIFICATION,
            BackendCapability.STREAMING,
            BackendCapability.PAGED_KV_CACHE,
            BackendCapability.GRAPH_EXECUTION,
            BackendCapability.CUSTOM_SYNCHRONIZATION,
        }

    @property
    def descriptor(self) -> BackendDescriptor:
        return self._descriptor

    def supports_capability(self, capability: str | BackendCapability) -> bool:
        if isinstance(capability, str):
            try:
                capability = BackendCapability(capability)
            except ValueError:
                return False
        return capability in self._capabilities

    def validate(self, physical_ir: PhysicalIR) -> BackendValidationResult:
        unsupported_ops: list[str] = []
        warnings: list[str] = []
        diagnostics: list[str] = []
        fallbacks: dict[str, str] = {}

        # 1. Check operations
        for op_id, op in physical_ir.operations.items():
            try:
                op_type = PhysicalOperationType(op.operation_type)
            except ValueError:
                unsupported_ops.append(op_id)
                diagnostics.append(f"Operation '{op_id}' has unknown type '{op.operation_type}'")
                continue

            if op_type.value not in self.descriptor.supported_execution_semantics:
                unsupported_ops.append(op_id)
                diagnostics.append(f"Operation '{op_id}' type '{op_type.value}' is not supported by MLX.")

        # 2. Check execution family compatibility
        for op_id, op in physical_ir.operations.items():
            if op.execution_family and op.execution_family not in self.descriptor.supported_execution_families:
                warnings.append(f"Operation '{op_id}' has execution family '{op.execution_family}' which is not explicitly listed in MLX supported families.")
                fallbacks[op_id] = "software_fallback"

        is_valid = len(unsupported_ops) == 0
        diagnostics.append(f"MLX validation status: {'PASSED' if is_valid else 'FAILED'}")

        return BackendValidationResult(
            is_valid=is_valid,
            unsupported_operations=tuple(unsupported_ops),
            unsupported_capabilities=tuple(),
            warnings=tuple(warnings),
            estimated_fallbacks=MappingProxyType(fallbacks),
            diagnostics=tuple(diagnostics)
        )

    def translate(self, physical_ir: PhysicalIR) -> TranslationResult:
        start_time = time.perf_counter()

        # Run validation
        val_result = self.validate(physical_ir)
        if not val_result.is_valid:
            raise ValueError(f"Physical IR validation failed for MLX: {val_result.diagnostics}")

        ops_dict = {}
        warnings: list[str] = list(val_result.warnings)
        diagnostics: list[str] = list(val_result.diagnostics)

        for op_id, op in physical_ir.operations.items():
            # Standard mapping of PhysicalOperationType to MLX subclasses
            op_type = PhysicalOperationType(op.operation_type)
            
            if op_type == PhysicalOperationType.FORWARD:
                mlx_op = MLXForwardOperation(
                    id=op.id,
                    inputs=op.inputs,
                    outputs=op.outputs,
                    dependencies=op.dependencies,
                    execution_family=op.execution_family,
                    metadata=op.metadata,
                )
            elif op_type == PhysicalOperationType.SAMPLING:
                mlx_op = MLXSamplingOperation(
                    id=op.id,
                    inputs=op.inputs,
                    outputs=op.outputs,
                    dependencies=op.dependencies,
                    execution_family=op.execution_family,
                    metadata=op.metadata,
                )
            elif op_type == PhysicalOperationType.CACHE_LOOKUP:
                mlx_op = MLXCacheLookupOperation(
                    id=op.id,
                    inputs=op.inputs,
                    outputs=op.outputs,
                    dependencies=op.dependencies,
                    execution_family=op.execution_family,
                    metadata=op.metadata,
                )
            elif op_type == PhysicalOperationType.CACHE_UPDATE:
                mlx_op = MLXCacheUpdateOperation(
                    id=op.id,
                    inputs=op.inputs,
                    outputs=op.outputs,
                    dependencies=op.dependencies,
                    execution_family=op.execution_family,
                    metadata=op.metadata,
                )
            elif op_type == PhysicalOperationType.SYNCHRONIZATION:
                mlx_op = MLXSynchronizationOperation(
                    id=op.id,
                    inputs=op.inputs,
                    outputs=op.outputs,
                    dependencies=op.dependencies,
                    execution_family=op.execution_family,
                    metadata=op.metadata,
                )
            else:
                mlx_op = MLXNoOpOperation(
                    id=op.id,
                    inputs=op.inputs,
                    outputs=op.outputs,
                    dependencies=op.dependencies,
                    execution_family=op.execution_family,
                    metadata=op.metadata,
                )
            ops_dict[op_id] = mlx_op

        backend_graph = BackendOperationGraph(
            backend_id=self.descriptor.backend_id,
            operations=MappingProxyType(ops_dict),
            roots=physical_ir.roots,
            metadata=MappingProxyType({"translation_layer": "MLXAdapter"}),
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        stats = {
            "translation_time_ms": elapsed_ms,
            "operation_count": len(ops_dict)
        }

        diagnostics.append(f"Successfully translated {len(ops_dict)} physical operations to MLX operation graph.")

        return TranslationResult(
            backend_graph=backend_graph,
            warnings=tuple(warnings),
            diagnostics=tuple(diagnostics),
            statistics=MappingProxyType(stats),
            backend_descriptor=self.descriptor
        )
