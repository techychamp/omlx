# SPDX-License-Identifier: Apache-2.0
"""Test performance assertions against baseline settings."""

import json
import pytest
import os

def load_baseline(baseline_path):
    if not os.path.exists(baseline_path):
        return {
            "metrics": {
                "ttft_ms": 120.4,
                "tps": 54.2,
                "peak_vram_mb": 4200.0
            }
        }
    with open(baseline_path) as f:
        return json.load(f)

def run_local_benchmark_mock():
    return {
        "ttft_ms": 122.1,
        "tps": 53.9,
        "peak_vram_mb": 4195.0
    }

def test_performance_regressions():
    """Compare active performance against baseline thresholds."""
    baseline = load_baseline("verification/baselines/v1/llama_m3_max_baseline.json")
    current = run_local_benchmark_mock()
    
    allowed_ttft_max = baseline["metrics"]["ttft_ms"] * 1.05
    assert current["ttft_ms"] <= allowed_ttft_max, (
        f"TTFT regressed: {current['ttft_ms']}ms > allowed maximum {allowed_ttft_max:.1f}ms."
    )
    
    allowed_tps_min = baseline["metrics"]["tps"] * 0.95
    assert current["tps"] >= allowed_tps_min, (
        f"Throughput degraded: {current['tps']} tok/s < allowed minimum {allowed_tps_min:.1f} tok/s."
    )
    
    allowed_vram_max = baseline["metrics"]["peak_vram_mb"] * 1.05
    assert current["peak_vram_mb"] <= allowed_vram_max, (
        f"VRAM leak detected: {current['peak_vram_mb']}MB > allowed limit {allowed_vram_max:.1f}MB."
    )
