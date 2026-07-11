import pytest
from types import MappingProxyType
from omlx.planner.compiler.backend.descriptor import BackendCapability, BackendDescriptor, BackendDescriptorRegistry
from omlx.planner.compiler.backend.adapter import MLXAdapter, BackendValidationResult, TranslationResult
from omlx.planner.ir.physical.graph import PhysicalIR
from omlx.planner.ir.physical.operations import PhysicalOperationType
from omlx.planner.ir.physical.operations import PhysicalOperation

def test_backend_descriptor_immutability():
    descriptor = BackendDescriptor(
        backend_id="test",
        backend_version="1.0",
        backend_family="test_fam",
        backend_generation="test_gen",
        supported_execution_semantics=(),
        supported_operation_mappings=(),
        supported_execution_families=(),
        supported_cache_layouts=(),
        supported_synchronization_primitives=(),
        supported_optimization_capabilities=(),
        supported_quantization_formats=(),
        supported_precision_formats=(),
        supported_cache_strategies=(),
        supported_execution_modes=(),
        supported_routing_strategies=(),
        supported_graph_features=(),
        hardware_capabilities=(),
        hardware_metadata=MappingProxyType({}),
        memory_model="test",
        memory_topology="test",
        execution_topology="test",
        stream_model="test",
        device_topology="test"
    )

    with pytest.raises(Exception):
        descriptor.backend_id = "new"

def test_mlx_adapter_capabilities():
    adapter = MLXAdapter()
    assert adapter.supports_capability(BackendCapability.AUTOREGRESSIVE)
    assert adapter.supports_capability("supports_autoregressive")
    assert not adapter.supports_capability(BackendCapability.EXPERT_ROUTING)

def test_mlx_adapter_validation():
    adapter = MLXAdapter()

    op = PhysicalOperation(
        id="op1",
        operation_type=PhysicalOperationType.FORWARD.value,
        inputs=(),
        outputs=(),
        dependencies=()
    )

    physical_ir = PhysicalIR(
        operations=MappingProxyType({"op1": op}),
        roots=("op1",),
        metadata=MappingProxyType({})
    )

    result = adapter.validate(physical_ir)
    assert isinstance(result, BackendValidationResult)
    assert result.is_valid
    assert len(result.unsupported_operations) == 0

def test_mlx_adapter_translation():
    adapter = MLXAdapter()

    op = PhysicalOperation(
        id="op1",
        operation_type=PhysicalOperationType.FORWARD.value,
        inputs=(),
        outputs=(),
        dependencies=()
    )

    physical_ir = PhysicalIR(
        operations=MappingProxyType({"op1": op}),
        roots=("op1",),
        metadata=MappingProxyType({})
    )

    result = adapter.translate(physical_ir)
    assert isinstance(result, TranslationResult)
    assert "MLXForwardOperation" in result.operation_statistics
    assert result.graph_statistics["total_nodes"] == 1
