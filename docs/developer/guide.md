# Developer Guide

## 1. System Requirements
*   **Platform:** Apple Silicon (M1/M2/M3/M4) is strictly required for the core Metal/MLX backend.
*   **Python:** Python 3.10 or higher.
*   **Dependencies:** Install development dependencies using `pip install -e ".[dev]"`.

## 2. Architecture Principles
As a contributor, you must adhere to the rules set forth in **RAES-015 (The Architectural Constitution)**:
*   **No Global State:** Do not introduce global singletons.
*   **Dependency Injection:** Mandates top-down flow, explicit state passing (e.g., using FastAPI `Depends`), and avoidance of service locators. Registries must be immutable post-boot.
*   **Immutability:** Use frozen dataclasses for descriptors, configuration, and IR nodes.
*   **Scheduler Isolation:** The Scheduler must remain agnostic to execution details.

## 3. Development Workflow

### Testing
*   **Fast Tests:** Run `pytest -m "not slow"` to execute the core test suite while skipping tests that require downloading or loading heavy model weights.
*   **Full Suite:** Run `pytest tests/` for a comprehensive check.
*   **Path Resolution:** When running tests manually, ensure local imports resolve correctly by prefixing the command: `PYTHONPATH=. pytest tests/<test_file>.py`.

### Repository Fitness Gates
The CI pipeline enforces strict Repository Fitness Gates:
*   Architecture compliance (e.g., verifying Scheduler isolation via AST parsing).
*   API stability.
*   Benchmark/memory regressions.
*   HuggingFace equivalence (Golden Tests).
*   Startup/shutdown/plugin validation.

### Technical Debt
Technical debt is tracked strictly via an Architectural Debt Register table, rather than scattered TODOs in the codebase.

## 4. Debugging Workflow
*   **Boot Sequences:** Because the Boot Phases are explicitly modeled as a State Machine (BOOTSTRAP -> CONFIGURATION -> etc.), boot failures are isolated to a specific phase, making root cause analysis straightforward.
*   **Failure Domains:** If a plugin causes a crash, it is disabled without taking down the server. If the Scheduler crashes, the Engine is restarted without terminating the process. Look for these isolation boundaries when checking logs.
