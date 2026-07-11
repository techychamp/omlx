import pytest
from types import MappingProxyType
from omlx.planner.domains.fusion.artifacts import (
    FusionGroup,
    FusionOpportunity,
    FusionDiagnostic,
    FusionCompatibilityReport,
    FusionStatistics,
    FusionPlan
)

def test_fusion_group_immutability():
    group = FusionGroup(id="test_group", node_ids=("node_1", "node_2"), fusion_type="TEST")
    with pytest.raises(Exception):
        group.id = "new_id"

def test_fusion_plan_defaults():
    plan = FusionPlan()
    assert len(plan.groups) == 0
    assert plan.statistics is None
    assert len(plan.diagnostics) == 0
