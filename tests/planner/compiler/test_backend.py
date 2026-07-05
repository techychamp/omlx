# SPDX-License-Identifier: Apache-2.0
"""
Tests for Backend Adapter Framework and registries.
"""
import pytest
import threading
from types import MappingProxyType
from omlx.planner.compiler.backend import (
    AdapterRegistry,
    BackendDescriptorRegistry,
    BackendDescriptor,
    BackendCapability,
    MLXAdapter,
    MLXForwardOperation,
    MLXSamplingOperation,
    MLXCacheLookupOperation,
    MLXCacheUpdateOperation,
    MLXSynchronizationOperation,
    MLXNoOpOperation,
    BaseBackendAdapter,
)
from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.ir.physical.operations import PhysicalOperation, PhysicalOperationType
from omlx.runtime.builder import RuntimeBuilder


class StubAdapter(BaseBackendAdapter):
    """Stub adapter for testing multiple registrations."""

    def __init__(self) -> None:
        self._descriptor = BackendDescriptor(
            backend_id="stub",
            backend_version="1.0.0",
            supported_execution_semantics=("forward", "noop"),
            supported_operation_mappings=("stub_forward", "stub_noop"),
            supported_execution_families=("autoregressive",),
            supported_cache_layouts=("none",),
            supported_synchronization_primitives=(),
            supported_optimization_capabilities=(),
            hardware_capabilities=(),
            memory_model="unified",
            execution_topology="single_node",
            backend_family="stub",
            backend_generation="stub",
            supported_quantization_formats=(),
            supported_precision_formats=(),
            supported_cache_strategies=(),
            supported_execution_modes=(),
            supported_routing_strategies=(),
            supported_graph_features=(),
            hardware_metadata=MappingProxyType({}),
            memory_topology="stub",
            stream_model="stub",
            device_topology="stub",

        )

    @property
    def descriptor(self) -> BackendDescriptor:
        return self._descriptor

    def validate(self, physical_ir):
        from omlx.planner.compiler.backend.adapter import BackendValidationResult
        return BackendValidationResult(is_valid=True)

    def translate(self, physical_ir):
        from omlx.planner.compiler.backend.adapter import TranslationResult
        from omlx.planner.compiler.backend.operations import BackendOperationGraph
        graph = BackendOperationGraph(
            backend_id="stub",
            operations=MappingProxyType({}),
            roots=physical_ir.roots,
        )
        return TranslationResult(backend_graph=graph, backend_descriptor=self.descriptor)

    def supports_capability(self, capability) -> bool:
        return False


def test_registry_lock_state():
    """Verify registry locking behavior in RuntimeBuilder."""
    builder = RuntimeBuilder()
    runtime = builder.build()

    # Registries must be locked on runtime startup
    assert runtime.adapter_registry is not None
    assert runtime.descriptor_registry is not None

    with pytest.raises(RuntimeError, match="AdapterRegistry is locked"):
        runtime.adapter_registry.register("mlx", "any", "autoregressive", "standard", MLXAdapter())

    with pytest.raises(RuntimeError, match="BackendDescriptorRegistry is locked"):
        runtime.descriptor_registry.register("dummy", MLXAdapter().descriptor)


def test_adapter_resolution():
    """Verify registry resolution behavior."""
    builder = RuntimeBuilder()
    runtime = builder.build()

    # Resolve active MLX adapter
    adapter = runtime.adapter_registry.resolve("mlx", "gpu", "autoregressive", "streaming")
    assert isinstance(adapter, MLXAdapter)

    # Resolution is case-insensitive
    adapter_case = runtime.adapter_registry.resolve("MLX", "GPU", "AUTOREGRESSIVE", "STREAMING")
    assert adapter_case is adapter

    # Unregistered target raises ValueError
    with pytest.raises(ValueError, match="No adapter registered"):
        runtime.adapter_registry.resolve("cuda", "gpu", "autoregressive", "standard")

