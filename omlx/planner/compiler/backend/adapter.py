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
    unsupported_execution_families: tuple[str, ...] = tuple()
    unsupported_execution_modes: tuple[str, ...] = tuple()
    unsupported_capabilities: tuple[str, ...] = tuple()
    unsupported_optimizations: tuple[str, ...] = tuple()
    unsupported_quantization_formats: tuple[str, ...] = tuple()
    unsupported_precision_formats: tuple[str, ...] = tuple()
    unsupported_graph_features: tuple[str, ...] = tuple()
    missing_capabilities: tuple[str, ...] = tuple()
    missing_synchronization: tuple[str, ...] = tuple()
    missing_routing: tuple[str, ...] = tuple()
    missing_cache_strategies: tuple[str, ...] = tuple()
    warnings: tuple[str, ...] = tuple()
    estimated_fallbacks: MappingProxyType[str, str] = field(default_factory=lambda: MappingProxyType({}))
    diagnostics: tuple[str, ...] = tuple()

@dataclass(frozen=True)
class TranslationResult:
    """Rich compilation results returned by backend translation."""
    backend_graph: BackendOperationGraph
    translation_latency: float = 0.0
    translation_warnings: tuple[str, ...] = tuple()
    operation_statistics: MappingProxyType[str, int] = field(default_factory=lambda: MappingProxyType({}))
    graph_statistics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    fallback_decisions: MappingProxyType[str, str] = field(default_factory=lambda: MappingProxyType({}))
    translation_metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    warnings: tuple[str, ...] = tuple()
    diagnostics: tuple[str, ...] = tuple()
    statistics: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    # Diagnostics Estimates
    estimated_execution_cost: float = 0.0
    estimated_memory_cost: float = 0.0
    estimated_synchronization_cost: float = 0.0
    estimated_graph_complexity: float = 0.0
    estimated_routing_complexity: float = 0.0
    estimated_cache_pressure: float = 0.0
    estimated_hardware_utilization: float = 0.0
    backend_descriptor: BackendDescriptor | None = field(default=None)

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
            backend_family="mlx",
            backend_generation="mlx_gen1",
            supported_execution_semantics=("forward", "sampling", "cache_lookup", "cache_update", "synchronization", "noop"),
            supported_operation_mappings=("mlx_forward", "mlx_sampling", "mlx_cache_lookup", "mlx_cache_update", "mlx_synchronization", "mlx_noop"),
            supported_execution_families=("autoregressive", "diffusion", "embedding"),
            supported_cache_layouts=("paged", "flat", "none"),
            supported_synchronization_primitives=("metal_synchronize",),
            supported_optimization_capabilities=("graph_compilation", "unified_memory"),
            supported_quantization_formats=("awq", "gptq"),
            supported_precision_formats=("fp16", "bf16", "fp32"),
            supported_cache_strategies=("rotating", "sliding_window"),
            supported_execution_modes=("eager", "compiled"),
            supported_routing_strategies=("static", "dynamic"),
            supported_graph_features=("control_flow", "loop_unrolling"),
            hardware_capabilities=("unified_memory", "apple_silicon"),
            hardware_metadata=MappingProxyType({"unified": True}),
            memory_model="unified",
            memory_topology="flat",
            execution_topology="single_node",
            stream_model="single_stream",
            device_topology="single_device",
            # Intelligence Metadata
            estimated_throughput=100.0,
            estimated_latency=10.0,
            estimated_memory_usage=2.5,
            peak_memory_estimate=4.0,
            memory_bandwidth_class="high",
            compute_class="high",
            supported_concurrency=4,
            graph_execution_efficiency=0.9,
            streaming_efficiency=0.95,
            speculative_execution_efficiency=0.8,
            expert_routing_efficiency=0.85,
            verification_efficiency=0.9,
            cache_efficiency=0.95,
            scheduler_compatibility=("continuous_batching", "static_batching"),
            precision_preferences=("fp16",),
            quantization_preferences=("awq",),
            hardware_preferences=("apple_silicon",),
            backend_maturity="production",

            # Quantization Metadata
            supported_quantization_families=("awq", "gptq"),
            preferred_quantization="awq",
            recommended_precision="fp16",
            mixed_precision_support=True,
            runtime_precision_switching=False,
            expert_quantization=False,
            diffusion_quantization=False,
            streaming_quantization=False,
            activation_quantization=False,
            weight_only_quantization=True,

            # Scheduling Metadata
            scheduling_characteristics=("continuous_batching", "async_execution", "graph_execution"),

            backend_metadata=MappingProxyType({
                "framework": "mlx",
                "device": "gpu",
                "supported_quantization_families": ("awq", "gptq"),
                "supported_quantization_layouts": ("int4", "int8"),
                "supported_calibration_methods": ("kl_div", "mse"),
                "supports_streaming_quantization": False,
                "supports_diffusion_quantization": False,
                "supports_moe_quantization": False,
                "supports_activation_quantization": False,
                "supports_weight_only_quantization": True,
                "supports_mixed_precision": True,
                "supports_runtime_quantization": False
            })
        )

        self._capabilities = {
            BackendCapability.AUTOREGRESSIVE,
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
            unsupported_execution_families=tuple(),
            unsupported_execution_modes=tuple(),
            unsupported_capabilities=tuple(),
            unsupported_optimizations=tuple(),
            unsupported_quantization_formats=tuple(),
            unsupported_precision_formats=tuple(),
            unsupported_graph_features=tuple(),
            missing_capabilities=tuple(),
            missing_synchronization=tuple(),
            missing_routing=tuple(),
            missing_cache_strategies=tuple(),
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
        op_counts: dict[str, int] = {}

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

            op_type_name = mlx_op.__class__.__name__
            op_counts[op_type_name] = op_counts.get(op_type_name, 0) + 1

        backend_graph = BackendOperationGraph(
            backend_id=self.descriptor.backend_id,
            operations=MappingProxyType(ops_dict),
            roots=physical_ir.roots,
            barriers=tuple(),
            synchronization_points=tuple(),
            metadata=MappingProxyType({"translation_layer": "MLXAdapter"}),
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        stats = {
            "translation_time_ms": elapsed_ms,
            "operation_count": len(ops_dict)
        }

        diagnostics.append(f"Successfully translated {len(ops_dict)} physical operations to MLX operation graph.")

        translation_latency = time.perf_counter() - start_time

        return TranslationResult(
            backend_graph=backend_graph,
            translation_latency=translation_latency,
            translation_warnings=tuple(warnings),
            operation_statistics=MappingProxyType(op_counts),
            graph_statistics=MappingProxyType({"total_nodes": len(ops_dict), "total_edges": sum(len(o.dependencies) for o in ops_dict.values())}),
            fallback_decisions=val_result.estimated_fallbacks,
            translation_metadata=MappingProxyType({"adapter": "MLXAdapter", "version": self.descriptor.backend_version}),
            warnings=tuple(warnings),
            diagnostics=tuple(diagnostics),
            statistics=MappingProxyType(stats),
            backend_descriptor=self.descriptor,

            estimated_execution_cost=0.0,
            estimated_memory_cost=0.0,
            estimated_synchronization_cost=0.0,
            estimated_graph_complexity=0.0,
            estimated_routing_complexity=0.0,
            estimated_cache_pressure=0.0,
            estimated_hardware_utilization=0.0,
        )
