# Performance Framework Spec

This specification details the **Performance Verification Framework** for oMLX. It covers the tracking metrics, execution environments, baseline storage formats, and testing methods to isolate performance regression risks.

---

## 1. Repository Layout Map

```
verification/
├── baselines/
│   ├── v1/
│   │   └── llama_m3_max_baseline.json     # Pinned performance metrics
│   ├── v2/
│   └── nightly/
└── scripts/
    ├── benchmark_runner.py                # Performs profile run and dumps JSON
    └── test_performance_assertions.py     # Pytest assertion tests
```

---

## 2. Performance Metrics Dictionary

Every performance audit must extract and validate the following metrics:

| Metric | Definition | Unit | Target Tolerance |
| :--- | :--- | :--- | :--- |
| **TTFT** | Time to First Token (prefill phase latency) | `ms` | <= 105% of baseline |
| **TPS** | Average generation throughput | `tok/s` | >= 95% of baseline |
| **Peak RAM** | Max Host Memory allocated during run | `MB` | <= 110% of baseline |
| **Peak VRAM** | Max Unified/Metal Memory allocated | `MB` | <= 105% of baseline |
| **P99 Latency** | 99th percentile of token-to-token delays | `ms` | <= 115% of baseline |
| **Prefill Time** | Net duration spent executing prefill | `ms` | <= 105% of baseline |
| **Decode Time** | Net duration spent executing decode steps | `ms` | <= 105% of baseline |
| **Scheduler Idle Time** | Time scheduler threads spent waiting for compute blocks | `ms` | <= 15ms per batch run |
| **Pipeline Utilization** | Percentage of time execution cores are active | `%` | >= 90% during load |
| **GPU Occupancy** | Active thread-group utilization rate on GPU | `%` | >= 80% during prefill |
| **Cache Reuse %** | Tokens matched in KV-cache index vs total prompt tokens | `%` | 100% on cache hits |
| **Verification Overhead** | CPU/Disk overhead added by verification hooks | `ms` | < 5% of total run duration |

---

## 3. Environment Capture Schema

All baselines and test reports must capture system hardware/software state to prevent configuration drift:

```json
{
  "macos_version": "macOS 15.1.0",
  "python_version": "3.11.8",
  "mlx_version": "0.31.2",
  "metal_version": "Metal 3.0",
  "chip_name": "Apple M3 Max",
  "gpu_cores": 40,
  "total_memory_gb": 64.0,
  "backend": "metal",
  "commit_sha": "d3b07384d113edecb226027a0528203f191b29a2",
  "quantization": "4bit"
}
```

---

## 4. Baseline Storage Format

Performance baselines are serialized to standard JSON conforming to `verification/schema/benchmark.schema.json`.

### Example Baseline JSON Output
```json
{
  "model_id": "Llama-3-8B-4bit",
  "execution_family": "dense_ar",
  "environment": {
    "macos_version": "macOS 15.1.0",
    "python_version": "3.11.8",
    "mlx_version": "0.31.2",
    "metal_version": "Metal 3.0",
    "chip_name": "Apple M3 Max",
    "total_memory_gb": 64.0,
    "backend": "metal",
    "commit_sha": "d3b07384d113edecb226027a0528203f191b29a2",
    "quantization": "4bit"
  },
  "metrics": {
    "ttft_ms": 120.4,
    "tps": 54.2,
    "peak_ram_mb": 240.0,
    "peak_vram_mb": 4200.0,
    "batch_efficiency": 98.4,
    "avg_latency_ms": 18.5,
    "p99_latency_ms": 22.0,
    "scheduler_idle_time_pct": 2.1,
    "pipeline_utilization_pct": 95.0,
    "gpu_occupancy_pct": 88.0,
    "cache_reuse_pct": 0.0,
    "prefill_time_ms": 100.0,
    "decode_time_ms": 2368.0,
    "verification_overhead_ms": 5.4
  }
}
```

---

## 5. Executable Pytest Template

This template tests regression tracking by comparing active runs to local JSON baselines.

```python
# verification/scripts/test_performance_assertions.py
# SPDX-License-Identifier: Apache-2.0

import json
import pytest
import os

# Helper to load baseline
def load_baseline(baseline_path):
    if not os.path.exists(baseline_path):
        # Fallback default baseline if not generated yet
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
    """Simulate current checkpoint metrics."""
    return {
        "ttft_ms": 122.1,
        "tps": 53.9,
        "peak_vram_mb": 4195.0
    }

def test_performance_regressions():
    """Compare active performance against baseline thresholds."""
    baseline = load_baseline("verification/baselines/v1/llama_m3_max_baseline.json")
    current = run_local_benchmark_mock()
    
    # Assert TTFT has not regressed by more than 5%
    allowed_ttft_max = baseline["metrics"]["ttft_ms"] * 1.05
    assert current["ttft_ms"] <= allowed_ttft_max, (
        f"TTFT regressed: {current['ttft_ms']}ms > allowed maximum {allowed_ttft_max:.1f}ms."
    )
    
    # Assert TPS has not dropped below 95% of baseline
    allowed_tps_min = baseline["metrics"]["tps"] * 0.95
    assert current["tps"] >= allowed_tps_min, (
        f"Throughput degraded: {current['tps']} tok/s < allowed minimum {allowed_tps_min:.1f} tok/s."
    )
    
    # Assert peak VRAM usage has not exceeded 105%
    allowed_vram_max = baseline["metrics"]["peak_vram_mb"] * 1.05
    assert current["peak_vram_mb"] <= allowed_vram_max, (
        f"VRAM leak detected: {current['peak_vram_mb']}MB > allowed limit {allowed_vram_max:.1f}MB."
    )
```

**Expected Test Output**:
```
pytest verification/scripts/test_performance_assertions.py -v
============================= test session starts ==============================
collected 1 item

verification/scripts/test_performance_assertions.py::test_performance_regressions PASSED

============================== 1 passed in 0.05s ===============================
```
