# Verification Execution Pipeline Spec

This specification describes the **Verification Execution Pipeline** that runs at every runtime checkpoint. It orchestrates sequential/parallel phases (Sanity check, Performance analysis, HuggingFace comparison, Regression analysis) to output a final dashboard report and Confidence Score.

---

## 1. Pipeline Execution Flow

```
   [Runtime Checkpoint / PR Commit]
                  │
                  ▼
      ┌───────────────────────┐
      │  Stage 1: Sanity      │ ──► [Fail: Exit 1]
      │  pytest -m "unit"     │
      └───────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │  Stage 2: Goldens     │ ──► [Fail: Exit 1]
      │  pytest golden_assets │
      └───────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │  Stage 3: Performance │ ──► [Fail: Exit 1]
      │  TPS/TTFT benchmark   │
      └───────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │  Stage 4: HF Equiv    │ ──► [Fail: Exit 1]
      │  Cosine/KL check      │
      └───────────────────────┘
                  │
                  ▼
      ┌───────────────────────┐
      │  Stage 5: Dashboard   │
      │  Calculate Score      │
      └───────────────────────┘
                  │
                  ▼
        [Verification Report]
```

---

## 2. Execution Stages & Commands

### Stage 1: Sanity Suite
*   **Command**: `pytest tests/ -m "not slow and not integration"`
*   **Target**: Basic code completeness, API routing, exception handling, and mock engine tests.
*   **Failure Threshold**: Any test failure blocks pipeline instantly.

### Stage 2: Golden Assets
*   **Command**: `pytest verification/scripts/test_golden_assets.py`
*   **Target**: Deterministic sequence generation, routing, and canvas reproduction under target seeds.
*   **Failure Threshold**: Mismatched tokens, image MSE shifts, or bad embeddings similarity.

### Stage 3: Performance Audit
*   **Command**: `python verification/scripts/run_benchmarks.py --model Llama-3-8B-4bit --output verification/reports/perf_temp.json`
*   **Target**: Measure TTFT, TPS, Peak RAM/VRAM, occupancy, P99 latency.
*   **Failure Threshold**: Performance regression > 5% on TTFT/TPS or Peak memory expansion > 10%.

### Stage 4: HF Equivalence Run
*   **Command**: `python verification/scripts/hf_equivalence_harness.py --model Llama-3-8B-4bit`
*   **Target**: Cosine similarity of intermediate tensors, KL divergence of output logit vectors.
*   **Failure Threshold**: Cosine similarity < 0.9999 or KL divergence > 1e-4.

### Stage 5: Regression Dashboard Generator
*   **Command**: `python verification/scripts/build_report.py --perf verification/reports/perf_temp.json --output verification/reports/checkpoint_report.json`
*   **Target**: Consolidate accuracy, performance, equivalence, and coverage scores into the final JSON dashboard.

---

## 3. Executable Pipeline Script

This mock pipeline script models how a CI/CD runner execution flow operates.

```python
# verification/scripts/pipeline_runner.py
# SPDX-License-Identifier: Apache-2.0

import subprocess
import sys
import json
import os

class PipelineRunner:
    def __init__(self, model_id):
        self.model_id = model_id
        self.report = {"stages": {}}

    def run_stage(self, name, command):
        print(f"Executing Stage: {name} ...")
        res = subprocess.run(command, shell=True, capture_output=True, text=True)
        success = res.returncode == 0
        self.report["stages"][name] = {
            "success": success,
            "exit_code": res.returncode,
            "stdout": res.stdout[-500:], # keep tail output
            "stderr": res.stderr[-500:]
        }
        if not success:
            print(f"Stage {name} FAILED with exit code {res.returncode}")
            print(res.stderr)
            return False
        print(f"Stage {name} PASSED.")
        return True

    def execute_all(self):
        # 1. Sanity
        if not self.run_stage("sanity_unit_tests", "pytest tests/ -m \"not slow and not integration\""):
            return False
        
        # 2. Golden validation
        if not self.run_stage("golden_assets", "pytest verification/scripts/test_golden_assets.py"):
            return False

        # 3. Equivalence assertions
        if not self.run_stage("equivalence_assertions", "pytest verification/scripts/test_equivalence_runner.py"):
            return False

        print("\nAll pipeline execution stages completed successfully.")
        return True

if __name__ == "__main__":
    runner = PipelineRunner("mock-llama-8b")
    # In practice: python verification/scripts/pipeline_runner.py
    success = runner.execute_all()
    sys.exit(0 if success else 1)
```

**Expected Executable Output**:
```
python verification/scripts/pipeline_runner.py
Executing Stage: sanity_unit_tests ...
Stage sanity_unit_tests PASSED.
Executing Stage: golden_assets ...
Stage golden_assets PASSED.
Executing Stage: equivalence_assertions ...
Stage equivalence_assertions PASSED.

All pipeline execution stages completed successfully.
```
