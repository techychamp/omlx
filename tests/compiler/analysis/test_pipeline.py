# SPDX-License-Identifier: Apache-2.0

import pytest
import tempfile
import json
from pathlib import Path
from types import MappingProxyType

from omlx.framework.model_intelligence.descriptor import ModelDescriptor
from omlx.planner.ir.graph import ExecutionIR
from omlx.planner.ir.nodes import IRNode, IRNodeType
from omlx.compiler.analysis import (
    AnalysisPipeline,
    AnalysisCache,
    CapabilityReport,
    ExecutionRequirements,
    AnalysisFingerprint
)
from omlx.compiler.analysis.graph import AnalysisGraph
from omlx.compiler.analysis.passes.semantic import SemanticAnalysisPass
from omlx.compiler.analysis.passes.capability import CapabilityPass
from omlx.compiler.analysis.passes.feature import FeatureDetectionPass
from omlx.compiler.analysis.passes.requirement import RequirementPass
from omlx.compiler.analysis.passes.diagnostics import DiagnosticsPass

@pytest.fixture
def dummy_descriptor():
    return ModelDescriptor(
        model_id="test/llama-3-8b",
        architecture="llama",
        task="chat",
        parameter_count=8_000_000_000,
        context_length=8192,
        tokenizer_family="llama",
        attention_type="gqa",
        kv_cache_support=True
    )

@pytest.fixture
def dummy_ir():
    nodes = {
        "node1": IRNode(id="node1", node_type=IRNodeType.ATTENTION, metadata=MappingProxyType({"rope": True, "rope_type": "dynamic"})),
        "node2": IRNode(id="node2", node_type=IRNodeType.FORWARD, metadata=MappingProxyType({"precision": "fp16"}))
    }
    return ExecutionIR(nodes=MappingProxyType(nodes), roots=("node2",))

def test_semantic_pass(dummy_descriptor, dummy_ir):
    graph = AnalysisGraph(dummy_descriptor, dummy_ir)
    p = SemanticAnalysisPass()
    res = p.run(graph)
    assert res["has_generative_loop"] is True
    assert res["is_pure_encoder"] is False

def test_capability_pass(dummy_descriptor, dummy_ir):
    graph = AnalysisGraph(dummy_descriptor, dummy_ir)
    p = CapabilityPass()
    res = p.run(graph)
    assert res["chat"] is True
    assert res["moe"] is False

def test_feature_pass(dummy_descriptor, dummy_ir):
    graph = AnalysisGraph(dummy_descriptor, dummy_ir)
    p = FeatureDetectionPass()
    res = p.run(graph)
    assert res["gqa"] is True
    assert res["rope"] == "dynamic"

def test_requirement_pass(dummy_descriptor, dummy_ir):
    graph = AnalysisGraph(dummy_descriptor, dummy_ir)
    p = RequirementPass()
    res = p.run(graph)

    assert "minimum_memory" in res["constraints"]
    assert "fp16" in res["constraints"]["required_precision"]
    assert "kv_cache" in res["dependencies"]

def test_diagnostics_pass():
    desc = ModelDescriptor(task="chat", tokenizer_family="")
    ir = ExecutionIR(nodes=MappingProxyType({
        "n1": IRNode(id="n1", node_type=IRNodeType.FORWARD, metadata=MappingProxyType({"unsupported": True}))
    }), roots=("n1",))

    graph = AnalysisGraph(desc, ir)
    p = DiagnosticsPass()
    res = p.run(graph)

    assert "missing_tokenizer" in res["unsupported"]
    assert "unsupported_operator:forward" in res["unsupported"]

def test_analysis_pipeline(dummy_descriptor, dummy_ir):
    with tempfile.TemporaryDirectory() as tmpdir:
        pipeline = AnalysisPipeline(use_cache=False)
        pipeline.cache = AnalysisCache(cache_dir=tmpdir)

        report = pipeline.analyze(dummy_descriptor, dummy_ir)

        assert report.architecture == "llama"
        assert report.requirements.capabilities["chat"] is True
        assert report.requirements.features["rope"] == "dynamic"
        assert "rotary_embedding" in report.requirements.dependencies

        # Test Cache hit
        report2 = pipeline.analyze(dummy_descriptor, dummy_ir)
        assert report2.architecture == report.architecture
        assert report2.fingerprint.model_hash == report.fingerprint.model_hash

def test_report_serialization():
    fp = AnalysisFingerprint("hash", "v1", "v1", "v1")
    req = ExecutionRequirements(
        capabilities=MappingProxyType({"chat": True}),
        constraints=MappingProxyType({"mem": "16G"})
    )
    report = CapabilityReport(fp, "llama", req, unsupported=("missing",))

    j = report.to_json()
    d = json.loads(j)

    report2 = CapabilityReport.from_dict(d)
    assert report2.architecture == "llama"
    assert report2.requirements.capabilities["chat"] is True
    assert "missing" in report2.unsupported
