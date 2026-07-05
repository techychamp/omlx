from typing import Dict, Any

class RepositoryHealthVerifier:
    def verify_compiler_health(self, invariants_passed: int, invariants_total: int) -> Dict[str, Any]:
        return {
            "status": "healthy" if invariants_passed == invariants_total else "unhealthy",
            "coverage": (invariants_passed / max(1, invariants_total)) * 100,
            "passed": invariants_passed,
            "total": invariants_total
        }

    def verify_backend_health(self, endpoints_passed: int, endpoints_total: int) -> Dict[str, Any]:
        return {
            "status": "healthy" if endpoints_passed == endpoints_total else "unhealthy",
            "coverage": (endpoints_passed / max(1, endpoints_total)) * 100,
            "passed": endpoints_passed,
            "total": endpoints_total
        }
