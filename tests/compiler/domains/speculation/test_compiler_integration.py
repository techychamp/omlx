import pytest
from types import MappingProxyType
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.compiler.planner import CompilerPlanner
from types import SimpleNamespace
from omlx.planner.domains.bundle import PlanningBundle
from omlx.planner.domains.speculation.artifacts import SpeculativeExecutionDescriptor
from omlx.planner.compiler.engine import CompilerEngine

def test_compiler_engine_speculation_integration():
    # Setup mock IR
    ir = ExecutionIR(
        nodes=MappingProxyType({}),

        roots=tuple()
    )

    # Setup Speculation Plan
    spec_plan = SpeculativeExecutionDescriptor(
        draft_model_id="draft_test",
        target_model_id="target_test",
        draft_length=2
    )

    # Create bundle with speculation plan
    bundle = PlanningBundle(speculation_plan=spec_plan)

    # Run compiler
    engine = CompilerEngine()

    # If the realization pass throws, this test will fail
    physical_ir = engine.compile(ir, planning_bundle=bundle)

    # PhysicalIR should be valid even if empty
    assert physical_ir is not None


def test_speculative_planner_integration():
    planner = CompilerPlanner()
    intent = SimpleNamespace(execution_mode='speculative', draft_model='A', target_model='B', draft_length=5)

    bundle = planner.compose_bundle(descriptor=None, execution_plan=None, strategy_intent=intent)

    assert bundle.speculation_plan is not None
    assert bundle.speculation_plan.draft_model_id == 'A'
    assert bundle.speculation_plan.target_model_id == 'B'
    assert bundle.speculation_plan.draft_length == 5
