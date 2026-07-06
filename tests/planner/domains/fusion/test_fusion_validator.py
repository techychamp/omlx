import pytest
from omlx.planner.domains.fusion.validator import FusionValidator
from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionGroup
from omlx.runtime.scheduling.artifacts import DependencyGraph
from types import MappingProxyType

def test_fusion_validator_valid():
    validator = FusionValidator()
    # Assuming empty graph means no nodes
    graph = DependencyGraph(operations={})
    plan = FusionPlan()
    assert validator.validate(plan, graph) is True

def test_fusion_validator_invalid_node():
    validator = FusionValidator()
    graph = DependencyGraph(operations={})
    group = FusionGroup(id="g1", node_ids=("missing_node",), fusion_type="T")
    plan = FusionPlan(groups=(group,))
    assert validator.validate(plan, graph) is False

def test_fusion_validator_valid_nodes():
    from omlx.runtime.scheduling.artifacts import DependencyGraph
    from omlx.planner.domains.fusion.validator import FusionValidator
    from omlx.planner.domains.fusion.artifacts import FusionPlan, FusionGroup

    graph = DependencyGraph(operations={"n1": {}, "n2": {}})
    plan = FusionPlan(groups=(FusionGroup(id="g1", node_ids=("n1", "n2"), fusion_type="TEST"),))
    validator = FusionValidator()
    assert validator.validate(plan, graph) is True
