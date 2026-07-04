from typing import Any
from omlx.planner.plan import ExecutionPlan
from omlx.capabilities.descriptor import ExecutionFamily

class PlannerValidationError(Exception):
    """Structured error for plan validation failures."""
    def __init__(self, message: str, errors: list[str]):
        super().__init__(message)
        self.errors = errors

def validate_plan(plan: ExecutionPlan) -> None:
    errors = []

    # Example validations
    if plan.execution_family not in [f.value for f in ExecutionFamily] and plan.execution_family not in ExecutionFamily:
        errors.append(f"Unsupported execution family: {plan.execution_family}")

    if plan.execution_backend == "":
        errors.append("Execution backend must be specified")

    # Check for backend/family compatibility
    if plan.execution_family == ExecutionFamily.AUTOREGRESSIVE and plan.execution_backend not in ("autoregressive", "speculative"):
         errors.append(f"Backend {plan.execution_backend} not compatible with {plan.execution_family}")

    if len(set(plan.optimization_passes)) != len(plan.optimization_passes):
        errors.append("Duplicate optimization passes detected")

    if errors:
        raise PlannerValidationError("Execution plan validation failed", errors)
