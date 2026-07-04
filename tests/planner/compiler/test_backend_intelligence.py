import pytest
from dataclasses import FrozenInstanceError

from omlx.planner.compiler.backend.intelligence.cost_models import (
    MemoryCostModel,
    LatencyCostModel,
    SynchronizationCostModel,
    TransferCostModel,
    CompilationCostModel,
    ExecutionCostModel,
    CacheCostModel,
    RoutingCostModel,
)
from omlx.planner.compiler.backend.intelligence.topology import (
    HardwareTopology,
    HardwareTopologyClass,
)
from omlx.planner.compiler.backend.intelligence.constraints import (
    ExecutionConstraints,
)
from omlx.planner.compiler.backend.intelligence.scoring import (
    BackendScoringFramework,
)
from omlx.planner.compiler.backend.descriptor import BackendDescriptor
from omlx.planner.compiler.backend.adapter import TranslationResult, BackendOperationGraph, MLXAdapter
from omlx.planner.ir.physical.graph import PhysicalIR

def test_cost_model_immutability():
    model = MemoryCostModel(base_memory_bytes=100)
    with pytest.raises(FrozenInstanceError):
        model.base_memory_bytes = 200

    lat_model = LatencyCostModel()
    with pytest.raises(FrozenInstanceError):
        lat_model.base_latency_ms = 10.0

def test_hardware_topology():
    topo = HardwareTopology(topology_class=HardwareTopologyClass.SINGLE_DEVICE)
    assert topo.topology_class == HardwareTopologyClass.SINGLE_DEVICE

    with pytest.raises(FrozenInstanceError):
        topo.node_count = 2

def test_execution_constraints():
    constraints = ExecutionConstraints(max_graph_size=100)
    assert constraints.max_graph_size == 100

    with pytest.raises(FrozenInstanceError):
        constraints.max_graph_size = 200

def test_scoring_framework():
    framework = BackendScoringFramework()
    # Dummy inputs for testing
    from types import MappingProxyType
    desc = BackendDescriptor(
        backend_id="dummy",
        backend_version="1.0",
        backend_family="dummy",
        backend_generation="gen1",
        supported_execution_semantics=tuple(),
        supported_operation_mappings=tuple(),
        supported_execution_families=("autoregressive",),
        supported_cache_layouts=tuple(),
        supported_synchronization_primitives=tuple(),
        supported_optimization_capabilities=tuple(),
        supported_quantization_formats=tuple(),
        supported_precision_formats=tuple(),
        supported_cache_strategies=tuple(),
        supported_execution_modes=tuple(),
        supported_routing_strategies=tuple(),
        supported_graph_features=tuple(),
        hardware_capabilities=tuple(),
        hardware_metadata=MappingProxyType({}),
        memory_model="",
        memory_topology="",
        execution_topology="",
        stream_model="",
        device_topology=""
    )

    ir = PhysicalIR(
        operations=MappingProxyType({}),
        roots=tuple(),
        metadata=MappingProxyType({})
    )
    constraints = ExecutionConstraints(preferred_execution_family="autoregressive")

    score = framework.compute_score(desc, ir, constraints)

    assert score.compatibility_score == 110.0
    assert score.memory_score == 50.0
    assert score.latency_score == 50.0
    assert score.throughput_score == 50.0
    assert "Matches preferred execution family." in score.reasons

def test_descriptor_immutability():
    from types import MappingProxyType
    desc = BackendDescriptor(
        backend_id="dummy",
        backend_version="1.0",
        backend_family="dummy",
        backend_generation="gen1",
        supported_execution_semantics=tuple(),
        supported_operation_mappings=tuple(),
        supported_execution_families=("autoregressive",),
        supported_cache_layouts=tuple(),
        supported_synchronization_primitives=tuple(),
        supported_optimization_capabilities=tuple(),
        supported_quantization_formats=tuple(),
        supported_precision_formats=tuple(),
        supported_cache_strategies=tuple(),
        supported_execution_modes=tuple(),
        supported_routing_strategies=tuple(),
        supported_graph_features=tuple(),
        hardware_capabilities=tuple(),
        hardware_metadata=MappingProxyType({}),
        memory_model="",
        memory_topology="",
        execution_topology="",
        stream_model="",
        device_topology=""
    )
    with pytest.raises(FrozenInstanceError):
        desc.backend_id = "other"

def test_translation_diagnostics():
    from types import MappingProxyType

    graph = BackendOperationGraph(
        backend_id="dummy",
        operations=MappingProxyType({}),
        roots=tuple(),
        barriers=tuple(),
        synchronization_points=tuple(),
        metadata=MappingProxyType({})
    )

    result = TranslationResult(
        backend_graph=graph,
        estimated_execution_cost=10.0,
        estimated_memory_cost=5.0
    )

    assert result.estimated_execution_cost == 10.0
    assert result.estimated_memory_cost == 5.0

    # Ensure MLXAdapter creates a valid TranslationResult
    adapter = MLXAdapter()

    ir = PhysicalIR(
        operations=MappingProxyType({}),
        roots=tuple(),
        metadata=MappingProxyType({})
    )
    tr = adapter.translate(ir)

    assert hasattr(tr, "estimated_execution_cost")
    assert hasattr(tr, "estimated_hardware_utilization")
