from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from omlx.planner.planner import ExecutionPlanner
from omlx.planner.plan import ExecutionPlan
from omlx.planner.bundle import PlanningBundle, MemoryPlan, CachePlan, VerificationPlan
from omlx.planner.device.artifacts import DevicePlan
from omlx.runtime.scheduling.artifacts import DependencyGraph, ExecutionPhase, DependencyBarrier, SynchronizationPoint

@dataclass(frozen=True)
class PlanningRequest:
    """Immutable request for planning."""
    model_id: str
    target_backend: Optional[str] = None
    constraints: Dict[str, Any] = field(default_factory=dict)

class PlanningClient:
    """API Client for Planning Domain."""

    def __init__(self, endpoint: str = "local"):
        self.endpoint = endpoint
        self._planner = ExecutionPlanner(
            backend_resolver=None,
            model_registry=None,
            policy_engine=None
        )

    def generate_bundle(self, request: PlanningRequest) -> PlanningBundle:
        """Generate a complete PlanningBundle for a request."""
        # This is a stub implementation for the API layer
        return PlanningBundle(
            execution_plan=ExecutionPlan(),
            device_plan=None,
            cache_plan=None,
            memory_plan=None,
            verification_plan=None
        )

    def extract_dependency_graph(self, bundle: PlanningBundle) -> DependencyGraph:
        """Extract a deterministic DependencyGraph from a PlanningBundle."""
        # Build phases based on plans
        phases = []

        # 1. Device phase (optional)
        if bundle.device_plan:
             phases.append(ExecutionPhase(
                 name="device_placement",
                 operations=["allocate_devices", "map_topology"],
                 barriers=[DependencyBarrier(name="device_ready")]
             ))

        # 2. Memory phase (optional)
        if bundle.memory_plan:
             phases.append(ExecutionPhase(
                 name="memory_allocation",
                 operations=["allocate_tensors", "setup_kv_cache"],
                 barriers=[DependencyBarrier(name="memory_ready")]
             ))

        # 3. Execution phase
        if bundle.execution_plan:
             # Basic mapping from ExecutionPlan steps if they exist
             ops = []
             if hasattr(bundle.execution_plan, 'steps'):
                 ops = getattr(bundle.execution_plan, 'steps')
             else:
                 ops = ["execute_model"]

             phases.append(ExecutionPhase(
                 name="compute",
                 operations=ops,
                 sync_points=[SynchronizationPoint(name="compute_done")]
             ))

        return DependencyGraph(
            operations={op: {"type": "abstract"} for p in phases for op in p.operations},
            phases=phases,
            metadata={"source": "PlanningBundle"}
        )
