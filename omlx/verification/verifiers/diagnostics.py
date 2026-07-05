from typing import Dict, Any

class DiagnosticsGenerator:
    def generate_compiler_invariant_report(self, verifier_results: Dict[str, bool]) -> Dict[str, Any]:
        passed = sum(1 for v in verifier_results.values() if v)
        return {
            "report": "compiler_invariants",
            "passed": passed,
            "failed": len(verifier_results) - passed,
            "total": len(verifier_results),
            "details": verifier_results
        }

    def generate_determinism_report(self, comparisons: int, failures: int) -> Dict[str, Any]:
        return {
            "report": "determinism",
            "comparisons": comparisons,
            "failures": failures,
            "deterministic": failures == 0
        }
