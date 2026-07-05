# SPDX-License-Identifier: Apache-2.0
"""
IR Builder
"""

from typing import Optional, TYPE_CHECKING, Dict, Any, List
from types import MappingProxyType
from typing import Any
from .nodes import IRNode, IRNodeType
from .graph import ExecutionIR
from .validation import validate_ir
from omlx.planner.compiler.cache.utils import compute_cache_key
if TYPE_CHECKING:
    from omlx.planner.compiler.dependency_tracker import DependencyTracker
if TYPE_CHECKING:
    from omlx.planner.compiler.cache.manager import CompilerCacheManager

class IRBuilder:
    """Builds an ExecutionIR from an ExecutionPlan."""
    def __init__(self, cache_manager: Optional['CompilerCacheManager'] = None, dependency_tracker: Optional['DependencyTracker'] = None):
        self.cache_manager = cache_manager
        self.dependency_tracker = dependency_tracker

    def build(self, plan: Any) -> ExecutionIR:
        """
        Lowers the ExecutionPlan into an ExecutionIR DAG.
        """
        cache_key = compute_cache_key("ir", plan)
        if self.cache_manager:
            cached = self.cache_manager.get(cache_key)
            if cached:
                return cached.value

        nodes: Dict[str, IRNode] = {}
        roots: List[str] = []

        # Simple mapping for now based on execution mode
        if plan.execution_mode in ("autoregressive", "streaming"):
            # Autoregressive Graph: Prefill -> Sample -> Forward -> Emit -> Verify

            prefill_node = IRNode(
                id="node_prefill",
                node_type=IRNodeType.PREFILL,
                metadata=MappingProxyType({})
            )
            nodes[prefill_node.id] = prefill_node

            # Note: For dependencies we do forward -> sample -> forward...
            # This is a simplification for the initial design
            # In a real system, the dependencies are data dependencies

            # Since dependencies point backward (A depends on B),
            # Prefill is the root of the dependency tree.

            sample_node = IRNode(
                id="node_sample",
                node_type=IRNodeType.SAMPLE,
                dependencies=("node_prefill",),
                metadata=MappingProxyType({})
            )
            nodes[sample_node.id] = sample_node

            forward_node = IRNode(
                id="node_forward",
                node_type=IRNodeType.FORWARD,
                dependencies=("node_sample",),
                metadata=MappingProxyType({})
            )
            nodes[forward_node.id] = forward_node

            verify_node = IRNode(
                id="node_verify",
                node_type=IRNodeType.VERIFY,
                dependencies=("node_forward",),
                metadata=MappingProxyType({})
            )
            nodes[verify_node.id] = verify_node

            emit_node = IRNode(
                id="node_emit",
                node_type=IRNodeType.EMIT,
                dependencies=("node_verify",),
                metadata=MappingProxyType({})
            )
            nodes[emit_node.id] = emit_node

            # The root of the execution (last node to execute if evaluating lazily,
            # or the sink of the graph)
            roots.append("node_emit")

        elif plan.execution_mode == "speculative":
             prefill_node = IRNode(
                id="node_prefill",
                node_type=IRNodeType.PREFILL,
                metadata=MappingProxyType({})
            )
             nodes[prefill_node.id] = prefill_node

             draft_node = IRNode(
                 id="node_draft",
                 node_type=IRNodeType.FORWARD,
                 dependencies=("node_prefill",),
                 metadata=MappingProxyType({"role": "draft"})
             )
             nodes[draft_node.id] = draft_node

             verify_node = IRNode(
                id="node_verify",
                node_type=IRNodeType.VERIFY,
                dependencies=("node_draft",),
                metadata=MappingProxyType({})
             )
             nodes[verify_node.id] = verify_node

             emit_node = IRNode(
                id="node_emit",
                node_type=IRNodeType.EMIT,
                dependencies=("node_verify",),
                metadata=MappingProxyType({})
             )
             nodes[emit_node.id] = emit_node
             roots.append("node_emit")

        elif plan.execution_mode == "diffusion":
             prefill_node = IRNode(
                id="node_prefill",
                node_type=IRNodeType.PREFILL,
                metadata=MappingProxyType({})
            )
             nodes[prefill_node.id] = prefill_node

             denoise_node = IRNode(
                 id="node_denoise",
                 node_type=IRNodeType.FORWARD,
                 dependencies=("node_prefill",),
                 metadata=MappingProxyType({"role": "denoise"})
             )
             nodes[denoise_node.id] = denoise_node

             emit_node = IRNode(
                id="node_emit",
                node_type=IRNodeType.EMIT,
                dependencies=("node_denoise",),
                metadata=MappingProxyType({})
             )
             nodes[emit_node.id] = emit_node
             roots.append("node_emit")

        else:
             prefill_node = IRNode(
                id="node_prefill",
                node_type=IRNodeType.PREFILL,
                metadata=MappingProxyType({})
            )
             nodes[prefill_node.id] = prefill_node
             roots.append("node_prefill")

        ir = ExecutionIR(
            nodes=MappingProxyType(nodes),
            roots=tuple(roots),
            metadata=MappingProxyType({
                "execution_mode": plan.execution_mode,
                "execution_backend": plan.execution_backend,
            })
        )

        # Inject cache key into metadata
        metadata = dict(ir.metadata)
        metadata["cache_key"] = cache_key
        object.__setattr__(ir, "metadata", metadata)

        validate_ir(ir)

        if self.cache_manager:
            self.cache_manager.put(cache_key, ir, size_bytes=4096, version="v1")
            if self.dependency_tracker:
                upstream_key = plan.planner_metadata.get("cache_key")
                if upstream_key:
                    self.dependency_tracker.record_dependency(upstream_key, cache_key)

        return ir
