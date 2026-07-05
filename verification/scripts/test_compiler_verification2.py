import pytest
from types import MappingProxyType
from omlx.verification.verifiers import (
    CompilerInvariantVerifier,
    OptimizationVerifier,
    ReplayVerifier,
    BackendEquivalenceVerifier,
    RepositoryHealthVerifier,
    DiagnosticsGenerator
)

class MockNode:
    def __init__(self, id, deps=None):
        self.id = id
        self.dependencies = deps or tuple()

class MockIR:
    def __init__(self, nodes, roots):
        self.nodes = nodes
        self.roots = roots

class MockAnalysis:
    def __init__(self, cache_key):
        self.metrics = {}
        self.metadata = {}
        self.cache_key = cache_key

class MockSession:
    def __init__(self, cache_key):
        self.metadata = {"cache_key": cache_key}

def test_compiler_invariants():
    verifier = CompilerInvariantVerifier()
    assert not verifier.verify_immutability({})
    assert not verifier.verify_immutability([])
    assert verifier.verify_immutability(MappingProxyType({}))
    assert verifier.verify_immutability(tuple())

    ir = MockIR(
        nodes={"a": MockNode("a"), "b": MockNode("b", deps=("a",))},
        roots=("b",)
    )
    assert verifier.verify_graph_consistency(ir)
    assert verifier.verify_operation_ordering(ir)
    assert verifier.verify_analysis_correctness(MockAnalysis("123"))

def test_optimization_correctness():
    verifier = OptimizationVerifier()
    ir1 = MockIR(nodes={}, roots=("b",))
    ir2 = MockIR(nodes={}, roots=("b",))
    assert verifier.verify_semantics_preserved(ir1, ir2)
    assert verifier.verify_analysis_reuse(MockAnalysis("123"), MockAnalysis("123"))

def test_replay_correctness():
    verifier = ReplayVerifier()
    assert verifier.verify_compiler_session_replay(MockSession("abc"), MockSession("abc"))

def test_backend_equivalence():
    verifier = BackendEquivalenceVerifier()
    ir1 = MockIR(nodes={"a": MockNode("a")}, roots=("a",))
    ir2 = MockIR(nodes={"b": MockNode("b")}, roots=("a",))
    assert verifier.verify_translation_consistency(ir1, ir2)
    assert verifier.verify_backend_graph_correctness(ir1, ir2)

def test_repository_health():
    verifier = RepositoryHealthVerifier()
    assert verifier.verify_compiler_health(10, 10)["status"] == "healthy"
    assert verifier.verify_backend_health(5, 5)["status"] == "healthy"

def test_diagnostics_generation():
    generator = DiagnosticsGenerator()
    rep1 = generator.generate_compiler_invariant_report({"test": True})
    assert rep1["passed"] == 1
    rep2 = generator.generate_determinism_report(100, 0)
    assert rep2["deterministic"] is True
