import abc
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Callable, Sequence

from .artifacts import GraphDiagnostic, GraphNode, GraphEdge
from .descriptor import GraphDescriptor


@dataclass(frozen=True)
class TransformationDiagnostic:
    level: str
    message: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class TransformationValidationReport:
    is_valid: bool
    diagnostics: tuple[TransformationDiagnostic, ...] = tuple()

@dataclass(frozen=True)
class TransformationStatistics:
    nodes_added: int = 0
    nodes_removed: int = 0
    nodes_replaced: int = 0
    edges_added: int = 0
    edges_removed: int = 0
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class TransformationDescriptor:
    id: str
    description: str
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

@dataclass(frozen=True)
class TransformationContext:
    metadata: MappingProxyType[str, Any] = field(default_factory=lambda: MappingProxyType({}))

class TransformationPass(abc.ABC):
    @property
    @abc.abstractmethod
    def descriptor(self) -> TransformationDescriptor:
        pass

    @abc.abstractmethod
    def apply(self, graph: GraphDescriptor, context: TransformationContext) -> tuple[GraphDescriptor, TransformationStatistics]:
        pass

class TransformationValidator(abc.ABC):
    @abc.abstractmethod
    def validate(self, original_graph: GraphDescriptor, transformed_graph: GraphDescriptor) -> TransformationValidationReport:
        pass

@dataclass(frozen=True)
class TransformationPipeline:
    passes: tuple[TransformationPass, ...] = tuple()
    validators: tuple[TransformationValidator, ...] = tuple()

    def execute(self, graph: GraphDescriptor, context: TransformationContext) -> tuple[GraphDescriptor, TransformationStatistics, TransformationValidationReport]:
        current_graph = graph
        total_stats = TransformationStatistics()

        for t_pass in self.passes:
            current_graph, pass_stats = t_pass.apply(current_graph, context)
            total_stats = TransformationStatistics(
                nodes_added=total_stats.nodes_added + pass_stats.nodes_added,
                nodes_removed=total_stats.nodes_removed + pass_stats.nodes_removed,
                nodes_replaced=total_stats.nodes_replaced + pass_stats.nodes_replaced,
                edges_added=total_stats.edges_added + pass_stats.edges_added,
                edges_removed=total_stats.edges_removed + pass_stats.edges_removed,
                metadata=MappingProxyType({**total_stats.metadata, **pass_stats.metadata})
            )

        diagnostics = []
        is_valid = True
        for validator in self.validators:
            report = validator.validate(graph, current_graph)
            if not report.is_valid:
                is_valid = False
            diagnostics.extend(report.diagnostics)

        return current_graph, total_stats, TransformationValidationReport(is_valid=is_valid, diagnostics=tuple(diagnostics))

class GraphRewriter:
    @staticmethod
    def replace_node(graph: GraphDescriptor, node_id: str, new_node: GraphNode) -> tuple[GraphDescriptor, TransformationStatistics]:
        if node_id not in graph.nodes:
            return graph, TransformationStatistics()

        nodes = dict(graph.nodes)
        nodes[new_node.id] = new_node
        if node_id != new_node.id:
            del nodes[node_id]

        edges = list(graph.edges)
        if node_id != new_node.id:
            for i, edge in enumerate(edges):
                if edge.source_id == node_id:
                    edges[i] = GraphEdge(source_id=new_node.id, target_id=edge.target_id, metadata=edge.metadata)
                if edge.target_id == node_id:
                    edges[i] = GraphEdge(source_id=edge.source_id, target_id=new_node.id, metadata=edge.metadata)

        return GraphDescriptor(id=graph.id, nodes=MappingProxyType(nodes), edges=tuple(edges), metadata=graph.metadata), TransformationStatistics(nodes_replaced=1)

    @staticmethod
    def insert_node(graph: GraphDescriptor, node: GraphNode) -> tuple[GraphDescriptor, TransformationStatistics]:
        if node.id in graph.nodes:
            return graph, TransformationStatistics()

        nodes = dict(graph.nodes)
        nodes[node.id] = node
        return GraphDescriptor(id=graph.id, nodes=MappingProxyType(nodes), edges=graph.edges, metadata=graph.metadata), TransformationStatistics(nodes_added=1)

    @staticmethod
    def remove_node(graph: GraphDescriptor, node_id: str) -> tuple[GraphDescriptor, TransformationStatistics]:
        if node_id not in graph.nodes:
            return graph, TransformationStatistics()

        nodes = dict(graph.nodes)
        del nodes[node_id]

        edges = [e for e in graph.edges if e.source_id != node_id and e.target_id != node_id]
        removed_edges = len(graph.edges) - len(edges)

        return GraphDescriptor(id=graph.id, nodes=MappingProxyType(nodes), edges=tuple(edges), metadata=graph.metadata), TransformationStatistics(nodes_removed=1, edges_removed=removed_edges)

    @staticmethod
    def rewire_edge(graph: GraphDescriptor, old_edge: GraphEdge, new_edge: GraphEdge) -> tuple[GraphDescriptor, TransformationStatistics]:
        if old_edge not in graph.edges:
            return graph, TransformationStatistics()

        edges = list(graph.edges)
        edges.remove(old_edge)
        edges.append(new_edge)

        return GraphDescriptor(id=graph.id, nodes=graph.nodes, edges=tuple(edges), metadata=graph.metadata), TransformationStatistics(edges_added=1, edges_removed=1)

    @staticmethod
    def clone_graph(graph: GraphDescriptor, new_id: str) -> GraphDescriptor:
        return GraphDescriptor(id=new_id, nodes=graph.nodes, edges=graph.edges, metadata=graph.metadata)

    @staticmethod
    def normalize_graph(graph: GraphDescriptor) -> tuple[GraphDescriptor, TransformationStatistics]:
        sorted_edges = tuple(sorted(graph.edges, key=lambda e: (e.source_id, e.target_id)))
        if sorted_edges == graph.edges:
            return graph, TransformationStatistics()
        return GraphDescriptor(id=graph.id, nodes=graph.nodes, edges=sorted_edges, metadata=graph.metadata), TransformationStatistics()
