# SPDX-License-Identifier: Apache-2.0
import pytest
from omlx.optimization.intelligence.profitability import OptimizationProfitabilityAnalysis

def test_profitability_analysis():
    analysis = OptimizationProfitabilityAnalysis(
        is_profitable=True,
        expected_gain_ms=5.0,
        expected_memory_reduction_bytes=2048
    )
    assert analysis.is_profitable is True
    assert analysis.expected_gain_ms == 5.0
    assert analysis.expected_memory_reduction_bytes == 2048

def test_profitability_analysis_immutability():
    analysis = OptimizationProfitabilityAnalysis(is_profitable=False)
    with pytest.raises(Exception):
        analysis.is_profitable = True
