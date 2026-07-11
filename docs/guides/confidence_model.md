# Confidence Model Spec

This specification details the **Verification Confidence Model** for oMLX. It establishes a repeatable, weighted metrics algorithm that grades every runtime checkpoint on a scale of `0%` to `100%` and assigns a verification maturity level.

---

## 1. Score Allocation & Weight Distribution

The confidence score is computed as:

$$\text{Confidence Score} = \sum_{k} W_k \times S_k$$

Where $W_k$ represents the category weight and $S_k$ is the normalized score ($0 \dots 100$) of that category.

| Category | Weight | Description | Metric Basis |
| :--- | :--- | :--- | :--- |
| **Correctness** | `35%` | Basic functional accuracy | Percentage of passing golden asset runs (prompts, images, embeddings) |
| **Architecture** | `20%` | Module ownership & runtime boundary constraints | Invariant compliance audits (e.g. no illegal scheduler dependencies) |
| **Regression** | `20%` | Structural comparison against baseline metrics | Number of metrics degrading more than allowed tolerance |
| **Performance** | `15%` | Latency and throughput compliance | Measured TTFT and TPS scores normalized against baselines |
| **Coverage** | `10%` | Test line coverage on modified files | Pytest-cov reports mapping to changed files |

---

## 2. Confidence Metrics Mapping

### Category 1: Correctness (35% Weight)
*   **Formula**: $S_{\text{correctness}} = \frac{\text{Passed Golden Tests}}{\text{Total Golden Tests}} \times 100$
*   **Metric**: Evaluates standard and custom evaluation datasets (MMLU, GSM8K, seed-based outputs).

### Category 2: Architecture Compliance (20% Weight)
*   **Formula**: $S_{\text{architecture}} = 100 - (20 \times \text{Violations})$
*   **Metric**: Static check of dependency graphs (no scheduler modifications, capabilities rules obeyed, correct plugins).

### Category 3: Regression Status (20% Weight)
*   **Formula**: $S_{\text{regression}} = 100 - (10 \times \text{Regressed Metrics})$
*   **Metric**: Compares performance/accuracy delta to baseline. Any metric exceeding tolerance degrades score.

### Category 4: Performance Latency (15% Weight)
*   **Formula**: $S_{\text{performance}} = \text{Min}\left(100, \frac{\text{TPS}_{\text{current}}}{\text{TPS}_{\text{baseline}}} \times 100\right)$
*   **Metric**: Evaluates TTFT, TPS, Peak VRAM, and occupancy metrics.

### Category 5: Coverage (10% Weight)
*   **Formula**: $S_{\text{coverage}} = \text{Branch Coverage \% of touched files}$
*   **Metric**: Verified through `pytest-cov` on touched lines of code.

---

## 3. Repeatable Level Scoring (Maturity Grade)

Based on the computed score and achieved metrics, the checkpoint is assigned a **Maturity Level**:

*   **Level 5: Production Grade** (Score >= 95% AND 100% Correctness AND no regressions)
*   **Level 4: Stable Release** (Score >= 85% AND 100% Correctness)
*   **Level 3: Validation Stage** (Score >= 70% AND hidden states matched)
*   **Level 2: Build Verification** (Score >= 50% AND compiles cleanly)
*   **Level 1: Unverified Alpha** (Score >= 30% AND unit tests pass)
*   **Level 0: Broken Draft** (Score < 30%)

---

## 4. Executable Python Scorer

This script loads raw evaluation stats and prints the structured report.

```python
# verification/scripts/calculate_confidence.py
# SPDX-License-Identifier: Apache-2.0

import json
import sys

def calculate_confidence_score(report_data):
    scores = report_data["scores"]
    weights = {
        "correctness": 0.35,
        "architecture": 0.20,
        "regression": 0.20,
        "performance": 0.15,
        "coverage": 0.10
    }
    
    total_score = sum(scores[key] * weights[key] for key in weights)
    
    # Assign Level
    level = 0
    if total_score >= 95.0 and scores["correctness"] == 100.0 and scores["regression"] == 100.0:
        level = 5
    elif total_score >= 85.0 and scores["correctness"] == 100.0:
        level = 4
    elif total_score >= 70.0:
        level = 3
    elif total_score >= 50.0:
        level = 2
    elif total_score >= 30.0:
        level = 1
        
    return round(total_score, 2), level

if __name__ == "__main__":
    # Simulated pipeline metrics payload
    mock_payload = {
        "checkpoint_id": "check-98ab21",
        "scores": {
            "correctness": 100.0,  # 100% golden tests passed
            "architecture": 100.0, # 0 violations
            "regression": 100.0,   # No degradations
            "performance": 95.0,   # 95% of baseline throughput
            "coverage": 80.0       # 80% coverage on touched lines
        }
    }
    
    score, level = calculate_confidence_score(mock_payload)
    
    report = {
        "checkpoint_id": mock_payload["checkpoint_id"],
        "weighted_confidence_score": score,
        "verification_level": level,
        "status": "APPROVED" if level >= 4 else "FAILED"
    }
    
    print(json.dumps(report, indent=2))
```

**Expected Runner Output**:
```
python verification/scripts/calculate_confidence.py
{
  "checkpoint_id": "check-98ab21",
  "weighted_confidence_score": 97.25,
  "verification_level": 5,
  "status": "APPROVED"
}
```
