# Verification Automation Spec

This specification describes the integration of the **Scientific Verification Architecture** into the CI/CD pipeline, detailing pull request checkpoints, baseline updates, and reporting flows.

---

## 1. Automation Pipeline Flow

```
                     [Pull Request Created]
                                │
                                ▼
                 [Verify Checkpoint Changeset]
                                │
                                ▼
             [Launch Runner VM / Apple Silicon Node]
                                │
                                ▼
            [Pull Baseline Metrics (nightly / nightly-v1)]
                                │
                                ▼
         [Execute verification/scripts/pipeline_runner.py]
                                │
                                ▼
                [Generate Checkpoint Report JSON]
                                │
                                ▼
               [Calculate Confidence Score & Level]
                                │
                               ▼
            Score >= 85% AND Level >= 4?
               ├── Yes ──► [Merge PR Approved] ──► [Optionally Update Baseline]
               └── No  ──► [Merge PR Blocked] ──► [Trigger Architectural Review]
```

---

## 2. CI/CD Integration Guide

### 1. Change Triage Rules
*   **PR Targets `omlx/` Core**: Full verification required (Sanity + Goldens + Performance + Equivalence).
*   **PR Targets Documentation/Tests only**: Execute Sanity + Coverage verification only.
*   **PR Targets Experimental Modules**: Full verification, but exclude from official community benchmark leaderboard uploads.

### 2. Baseline Promotion Protocol
When a PR introduces an intentional performance optimization (e.g. implementing custom kernels, improving cache strategy), baseline parameters must be updated:
1. Run target benchmark: `python verification/scripts/run_benchmarks.py --update`
2. Validate output schema: `jsonschema -i verification/baselines/nightly/llama_baseline.json verification/schema/benchmark.schema.json`
3. Commit new baseline alongside the optimization code.

---

## 3. GitHub Action Workflow Design

The following YAML outlines the GitHub Action mapping for repository checkpoints.

```yaml
# .github/workflows/verification.yml
name: Scientific Verification Pipeline

on:
  pull_request:
    branches: [ main ]
    paths:
      - 'omlx/**'
      - 'verification/**'

jobs:
  verify:
    runs-on: self-hosted-macOS-silicon
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov jsonschema numpy

      - name: Run Verification Pipeline
        run: |
          python verification/scripts/pipeline_runner.py

      - name: Compute Checkpoint Grade
        run: |
          python verification/scripts/calculate_confidence.py > verification/reports/report.json
          cat verification/reports/report.json

      - name: Validate Report Schema
        run: |
          python -c "
          import json, jsonschema
          with open('verification/reports/report.json') as f: report = json.load(f)
          with open('verification/schema/confidence.schema.json') as f: schema = json.load(f)
          jsonschema.validate(instance=report, schema=schema)
          print('Report Schema Validation: PASS')
          "
```
