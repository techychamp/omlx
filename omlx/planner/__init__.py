"""
Execution Planner architecture.
Transforms a CapabilityDescriptor into an immutable ExecutionPlan.
"""

from .plan import ExecutionPlan
from .planner import ExecutionPlanner
from .passes import PlanningPass, PassRegistry

__all__ = [
    "ExecutionPlan",
    "ExecutionPlanner",
    "PlanningPass",
    "PassRegistry",
]
