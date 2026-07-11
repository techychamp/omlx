# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List, Set, Tuple
from types import MappingProxyType

from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.planner.domains.diffusion.artifacts.plan import DiffusionPlan
from .artifacts import (
    RealizedTimestepGraph,
    LatentExecutionGraph,
    ConditioningExecutionGraph,
    DiffusionRealizationDiagnostic,
    DiffusionRealizationStatistics,
    DiffusionValidationReport,
    DiffusionExecutionGraph,
    DiffusionRealizationReport,
)

class DiffusionRealizer:
    """
    Compiler-native realization of immutable DiffusionPlans into modified ExecutionIR.
    """
    def __init__(self):
        pass

    def realize(self, ir: ExecutionIR, plan: DiffusionPlan) -> Tuple[ExecutionIR, DiffusionRealizationReport]:
        """
        Transforms the given ExecutionIR according to the DiffusionPlan.
        """
        diagnostics = []
        new_nodes: Dict[str, IRNode] = {}
        realized_timesteps = []

        # 1. Latent Graph Realization
        latent_node = IRNode(
            id="diffusion_latent_init",
            node_type=IRNodeType.FORWARD,
            dependencies=tuple(),
            metadata=MappingProxyType({"diffusion_role": "latent", "latent_config": dict(plan.descriptor.latent.__dict__)})
        )
        new_nodes[latent_node.id] = latent_node
        latent_graph = LatentExecutionGraph(nodes=(latent_node,))

        # 2. Conditioning Graph Realization
        conditioning_node = IRNode(
            id="diffusion_conditioning",
            node_type=IRNodeType.FORWARD,
            dependencies=tuple(),
            metadata=MappingProxyType({"diffusion_role": "conditioning", "conditioning_config": dict(plan.descriptor.conditioning.__dict__)})
        )
        new_nodes[conditioning_node.id] = conditioning_node
        conditioning_graph = ConditioningExecutionGraph(nodes=(conditioning_node,))

        # 3. Timestep Graph Realization
        # We unroll the IR graph for each timestep

        # In a real unroll, the first step depends on the latent and conditioning.
        # Subsequent steps depend on the previous step.
        previous_step_roots = [latent_node.id, conditioning_node.id]

        for timestep in plan.timestep_schedule:
            current_step_nodes = []

            for nid, node in ir.nodes.items():
                new_id = f"{nid}_ts_{timestep}"

                # Rewire internal dependencies for this step
                new_deps = [f"{dep}_ts_{timestep}" for dep in node.dependencies]

                # If this node was a root in the original step (no dependencies),
                # it now depends on the previous step's roots
                if not node.dependencies:
                    new_deps.extend(previous_step_roots)

                new_node = IRNode(
                    id=new_id,
                    node_type=node.node_type,
                    dependencies=tuple(new_deps),
                    metadata=MappingProxyType({**node.metadata, "timestep": timestep})
                )
                new_nodes[new_id] = new_node
                current_step_nodes.append(new_node)

            # The roots of this timestep become the inputs for the next timestep
            previous_step_roots = [f"{root}_ts_{timestep}" for root in ir.roots]

            realized_timesteps.append(RealizedTimestepGraph(
                timestep=timestep,
                nodes=tuple(current_step_nodes)
            ))

        # The new roots of the entire transformed graph are the roots of the final timestep
        new_roots = previous_step_roots

        transformed_ir = ExecutionIR(
            nodes=MappingProxyType(new_nodes),
            roots=tuple(new_roots),
            metadata=ir.metadata
        )

        stats = DiffusionRealizationStatistics(
            original_node_count=len(ir.nodes),
            transformed_node_count=len(transformed_ir.nodes),
            timesteps_realized=len(plan.timestep_schedule)
        )

        validation = DiffusionValidationReport(
            is_valid=len(diagnostics) == 0,
            diagnostics=tuple(diagnostics)
        )

        execution_graph = DiffusionExecutionGraph(
            latent_graph=latent_graph,
            conditioning_graph=conditioning_graph,
            timesteps=tuple(realized_timesteps)
        )

        report = DiffusionRealizationReport(
            statistics=stats,
            validation_report=validation,
            execution_graph=execution_graph
        )

        return transformed_ir, report
