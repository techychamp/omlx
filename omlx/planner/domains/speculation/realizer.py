# SPDX-License-Identifier: Apache-2.0
"""
Compiler-Native Speculative Graph Realization Framework.
"""
import time
import uuid
from typing import Optional, List, Tuple
from types import MappingProxyType

from omlx.framework.graph.descriptor import GraphDescriptor, GraphNode, GraphEdge
from omlx.planner.domains.speculation.artifacts import (
    SpeculativeExecutionDescriptor,
    SpeculativeExecutionGraph,
    DraftExecutionGraph,
    VerificationExecutionGraph,
    AcceptanceExecutionGraph,
    SpeculativeRealizationReport,
    SpeculativeRealizationDiagnostic,
    SpeculativeRealizationStatistics,
)


class SpeculativeRealizer:
    """
    Realizes speculative execution plans into compiler-native speculative graphs.
    """

    def realize(
        self,
        descriptor: SpeculativeExecutionDescriptor,
        base_graph: Optional[GraphDescriptor] = None
    ) -> SpeculativeRealizationReport:
        """
        Realize a SpeculativeExecutionDescriptor into a SpeculativeExecutionGraph.
        """
        start_time = time.time()
        diagnostics: List[SpeculativeRealizationDiagnostic] = []

        try:
            # 1. Realize Draft Graph
            draft_graph = self._realize_draft(descriptor, base_graph)

            # 2. Realize Verification Graph
            verification_graph = self._realize_verification(descriptor, draft_graph.graph)

            # 3. Realize Acceptance Graph
            acceptance_graph = self._realize_acceptance(descriptor, verification_graph.graph)

            # 4. Construct Full Speculative Graph
            speculative_graph = SpeculativeExecutionGraph(
                id=f"speculative_graph_{uuid.uuid4().hex[:8]}",
                draft_graph=draft_graph,
                verification_graph=verification_graph,
                acceptance_graph=acceptance_graph,
                descriptor=descriptor
            )

            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            stats = SpeculativeRealizationStatistics(
                draft_node_count=len(draft_graph.graph.nodes),
                verification_node_count=len(verification_graph.graph.nodes),
                acceptance_node_count=len(acceptance_graph.graph.nodes),
                realization_latency_ms=latency_ms
            )

            return SpeculativeRealizationReport(
                success=True,
                speculative_graph=speculative_graph,
                statistics=stats,
                diagnostics=tuple(diagnostics)
            )

        except Exception as e:
            diagnostics.append(
                SpeculativeRealizationDiagnostic(
                    level="ERROR",
                    message=f"Speculative realization failed: {str(e)}"
                )
            )
            return SpeculativeRealizationReport(
                success=False,
                diagnostics=tuple(diagnostics)
            )

    def _realize_draft(self, descriptor: SpeculativeExecutionDescriptor, base_graph: Optional[GraphDescriptor]) -> DraftExecutionGraph:
        """Realize the draft generation execution graph."""
        nodes = {}
        edges = []

        # Simple mock realization for now. In a real system, this would map
        # descriptor operations into graph nodes based on the base_graph context.
        if base_graph:
            pass # Use base graph context

        draft_node = GraphNode(
            id="draft_generate",
            metadata=MappingProxyType({"operation": "generate", "model": descriptor.draft_model_id, "length": descriptor.draft_length})
        )
        nodes[draft_node.id] = draft_node

        graph_desc = GraphDescriptor(
            id=f"draft_graph_{uuid.uuid4().hex[:8]}",
            nodes=MappingProxyType(nodes),
            edges=tuple(edges)
        )

        return DraftExecutionGraph(
            id=f"draft_exec_{uuid.uuid4().hex[:8]}",
            graph=graph_desc
        )

    def _realize_verification(self, descriptor: SpeculativeExecutionDescriptor, base_graph: Optional[GraphDescriptor]) -> VerificationExecutionGraph:
        """Realize the target verification execution graph."""
        nodes = {}
        edges = []

        verify_node = GraphNode(
            id="target_verify",
            metadata=MappingProxyType({"operation": "verify", "model": descriptor.target_model_id})
        )
        nodes[verify_node.id] = verify_node

        graph_desc = GraphDescriptor(
            id=f"verify_graph_{uuid.uuid4().hex[:8]}",
            nodes=MappingProxyType(nodes),
            edges=tuple(edges)
        )

        return VerificationExecutionGraph(
            id=f"verify_exec_{uuid.uuid4().hex[:8]}",
            graph=graph_desc
        )

    def _realize_acceptance(self, descriptor: SpeculativeExecutionDescriptor, base_graph: Optional[GraphDescriptor]) -> AcceptanceExecutionGraph:
        """Realize the token acceptance evaluation execution graph."""
        nodes = {}
        edges = []

        accept_node = GraphNode(
            id="evaluate_acceptance",
            metadata=MappingProxyType({"operation": "accept", "strategy": "greedy"}) # Mock strategy
        )
        nodes[accept_node.id] = accept_node

        graph_desc = GraphDescriptor(
            id=f"accept_graph_{uuid.uuid4().hex[:8]}",
            nodes=MappingProxyType(nodes),
            edges=tuple(edges)
        )

        return AcceptanceExecutionGraph(
            id=f"accept_exec_{uuid.uuid4().hex[:8]}",
            graph=graph_desc
        )
