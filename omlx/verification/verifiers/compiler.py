from typing import Any, Dict, List, Set
from types import MappingProxyType

class CompilerInvariantVerifier:
    def verify_immutability(self, artifact: Any) -> bool:
        if isinstance(artifact, dict) and not isinstance(artifact, MappingProxyType):
            return False
        if isinstance(artifact, list) and not isinstance(artifact, tuple):
            return False
        return True

    def verify_graph_consistency(self, ir: Any) -> bool:
        if not hasattr(ir, "nodes") or not hasattr(ir, "roots"):
            return False

        # Verify roots exist
        for root in ir.roots:
            if root not in ir.nodes:
                return False

        # Verify all dependencies exist and check for cycles
        visited = set()
        path = set()

        def visit(node_id: str) -> bool:
            if node_id in path:
                return False # Cycle detected
            if node_id in visited:
                return True

            path.add(node_id)
            node = ir.nodes.get(node_id)
            if not node:
                return False

            for dep in getattr(node, "dependencies", tuple()):
                if not visit(dep):
                    return False

            path.remove(node_id)
            visited.add(node_id)
            return True

        for root in ir.roots:
            if not visit(root):
                return False

        return True

    def verify_operation_ordering(self, ir: Any) -> bool:
        # Simple topological sort check
        return self.verify_graph_consistency(ir)

    def verify_analysis_correctness(self, analysis: Any) -> bool:
        # Check standard analysis output structure
        return hasattr(analysis, "metrics") and hasattr(analysis, "metadata")

class OptimizationVerifier:
    def verify_semantics_preserved(self, pre_ir: Any, post_ir: Any) -> bool:
        # Check roots match
        if not hasattr(pre_ir, "roots") or not hasattr(post_ir, "roots"):
            return False
        return set(pre_ir.roots) == set(post_ir.roots)

    def verify_analysis_reuse(self, analysis1: Any, analysis2: Any) -> bool:
        if not hasattr(analysis1, "cache_key") or not hasattr(analysis2, "cache_key"):
            return False
        return analysis1.cache_key == analysis2.cache_key

class ReplayVerifier:
    def verify_compiler_session_replay(self, session1: Any, session2: Any) -> bool:
        if not hasattr(session1, "metadata") or not hasattr(session2, "metadata"):
            return False
        return session1.metadata.get("cache_key") == session2.metadata.get("cache_key")
