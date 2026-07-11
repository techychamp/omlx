# GitHub Actions Specifications

This document catalogs the inputs, parameters, environments, and matrix definitions of the oMLX composite actions and reusable workflows.

## 1. Reusable Workflows

### `architecture.yml`
- **Purpose**: Runs Ruff, Black, Isort, Mypy, and the `run_005_platform_validation.py` script.
- **Runs-on**: `macos-latest` (to compile and check SwiftUI View/ViewModel layer boundaries).

### `python-tests.yml`
- **Purpose**: Executes the pytest test suite in parallel.
- **Matrix**:
  - `os`: `[macos-latest]` (Ubuntu ready).
  - `python-version`: `['3.11', '3.12', '3.13']`.

### `swift-tests.yml`
- **Purpose**: Executes Xcode Swift tests.
- **Runs-on**: `macos-latest`.

### `packaging.yml`
- **Purpose**: Verifies python sdist/wheel builds and compiles `One.app`.
- **Runs-on**: `macos-latest`.

### `runtime-smoke.yml`
- **Purpose**: Starts the local FastAPI server, tests health checks, verifies endpoints return 200, and shuts down.
- **Runs-on**: `macos-latest`.

### `performance.yml`
- **Inputs**:
  - `strict`: `boolean` (default `false`). If true, fails the job on regression; if false, issues warnings only.

### `security.yml`
- **Jobs**:
  - `dependency-audit`: runs `pip-audit`.
  - `secret-scan`: checks for committed private keys.
  - `bandit`: runs static security analysis.
  - `license-audit`: verifies Apache license header coverage is >= 80%.

### `docs.yml`
- **Purpose**: Checks for broken markdown links and ensures milestone files exist.

---

## 2. Composite Actions

### `setup-python`
- **Inputs**:
  - `python-version` (default: `3.12`).
- **Steps**: Configures standard python and installs `uv` package manager with caching.

### `setup-swift`
- **Steps**: Selects the active Xcode command-line tools directory and prints active Swift/Xcode toolchains.

### `cache`
- **Inputs**:
  - `python-version` (default: `3.12`).
- **Steps**: Sets up multi-layer cache paths for `uv`, `SPM`, `DerivedData`, and `venvstacks` build/export trees.
