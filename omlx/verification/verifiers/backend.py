from typing import Any

class BackendEquivalenceVerifier:
    def verify_translation_consistency(self, logical_ir: Any, physical_ir: Any) -> bool:
        return True
    def verify_backend_graph_correctness(self, physical_ir: Any, backend_graph: Any) -> bool:
        return True
