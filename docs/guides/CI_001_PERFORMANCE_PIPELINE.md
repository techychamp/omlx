# Performance Regression Pipeline

This document explains how performance regressions are tracked and verified against baselines.

## 1. Metrics Collection
The performance test suite (`tests/test_performance_regression.py`) automatically gathers four core metrics:
- **Import Time**: The overhead of loading the `omlx` package in a clean python process.
- **Bundle Size**: The complete directory size of `One.app` (in MB).
- **Startup Time**: The duration required to launch the backend server and reach a successful HTTP 200 `/health` response.
- **Inference Metrics**: TTFT and TPS values (evaluated under test runs).

## 2. Versioned Baselines
Baseline metrics are stored as JSON files under `verification/baselines/performance/`.
This enables different machines or runner platforms to match their respective baseline profiles (e.g. `macos-m1.json`, `macos-intel.json`).

## 3. Pull Request vs. Nightly/Release Validation
To prevent transient changes from blocking developers:
- **Pull Requests**: The performance check runs in **non-strict mode** (`OMLX_PERF_STRICT=0`). If metrics exceed the baseline threshold, warnings are printed to the logs, but the CI status check remains green.
- **Nightly & Releases**: The check runs in **strict mode** (`OMLX_PERF_STRICT=1`). Any regression exceeding the configured margins (e.g. +15% import time, +10% bundle size, +20% startup time) will fail the CI check.
