# Engineering Checkpoint Map

This roadmap breaks down future work into isolated, verifiable, repository-specific micro-checkpoints. Large feature branches are forbidden. Every checkpoint must be independently testable and touch no more than 2-5 files.

## Phase 2: Execution Planning Layer

### Checkpoint 2.1: RAES-003 Execution Planning Architecture Audit
* **Goal**: Determine whether the existing architecture already supports an Execution Planner.
* **Purpose**: Avoid implementing a planner that duplicates existing abstractions.
* **Allowed Files**: `docs/architecture/`
* **Forbidden Files**: All runtime and test files.
* **Dependencies**: Completion of RAES-002.
* **Verification**: Review of design document against codebase.
* **Rollback Strategy**: Discard document.
* **Exit Criteria**: A design document answering: Where does it live? Can it reuse ExecutionGraph, CapabilityRegistry, ExecutionBackend? Can it avoid Scheduler/EngineCore changes? How are models expressed as plans? No runtime code changes.

### Checkpoint 2.2: Execution Planner Interface
* **Goal**: Define the abstract interfaces for `ExecutionPlanner` and `ExecutionPlan`.
* **Purpose**: Establish the core API for the Execution Planning layer.
* **Allowed Files**: `omlx/inference/planner.py` (new), `tests/test_planner.py`.
* **Forbidden Files**: Existing components (`omlx/scheduler.py`, `omlx/engine_core.py`, existing tests).
* **Dependencies**: Checkpoint 2.1 (Architecture Audit).
* **Verification**: Run `pytest tests/test_planner.py`.
* **Rollback Strategy**: Revert branch.
* **Exit Criteria**: Interfaces defined and mocked in tests. No integration.

## Phase 3: Execution Programs

### Checkpoint 3.1: Repository Analysis for AR/Diffusion
* **Goal**: Map existing backend capabilities to the new planner interface.
* **Purpose**: Prepare for integration without writing functional code.
* **Allowed Files**: `docs/architecture/`
* **Forbidden Files**: All runtime files.
* **Dependencies**: Checkpoint 2.2.
* **Verification**: Architecture review.
* **Rollback Strategy**: Discard document.
* **Exit Criteria**: Design document mapping capabilities to ExecutionGraph nodes.

### Checkpoint 3.2: Backend Interface Verification
* **Goal**: Ensure existing backends can accept a generated `ExecutionPlan` without behavior changes.
* **Purpose**: Validate the planner abstraction against existing code.
* **Allowed Files**: `omlx/inference/backends/base.py`.
* **Forbidden Files**: `omlx/inference/backends/autoregressive_backend.py`, tests logic.
* **Dependencies**: Checkpoint 3.1.
* **Verification**: Run entire test suite `pytest tests/`.
* **Rollback Strategy**: Revert branch.
* **Exit Criteria**: Abstract methods added/verified; tests pass.

### Checkpoint 3.3: Execution Program Registration
* **Goal**: Register basic execution modes (AR, Diffusion) into the capability registry.
* **Purpose**: Make the programs available for selection.
* **Allowed Files**: `omlx/registry/capability_registry.py`.
* **Forbidden Files**: Execution logic files.
* **Dependencies**: Checkpoint 3.2.
* **Verification**: Unit tests on capability registry.
* **Rollback Strategy**: Revert registry change.
* **Exit Criteria**: Registry accepts program types. No execution changes.

### Checkpoint 3.4: Execution Graph Integration
* **Goal**: Planner emits structural Execution Graphs for AR and Diffusion.
* **Purpose**: Connect the planner to the graph representation.
* **Allowed Files**: `omlx/inference/planner.py`, `omlx/inference/execution_graph.py`.
* **Forbidden Files**: Engine core and scheduler.
* **Dependencies**: Checkpoint 3.3.
* **Verification**: Unit tests `pytest tests/test_planner.py`.
* **Rollback Strategy**: Revert branch.
* **Exit Criteria**: Unit tests confirm accurate graph generation from mock capabilities.

### Checkpoint 3.5: Strategy Routing
* **Goal**: Engine routes execution through the Planner rather than hardcoded strategies.
* **Purpose**: Enable the planner in the real execution flow.
* **Allowed Files**: `omlx/engine_core.py`.
* **Forbidden Files**: API routes, Cache layer.
* **Dependencies**: Checkpoint 3.4.
* **Verification**: Run end-to-end integration tests `pytest tests/integration/`.
* **Rollback Strategy**: Revert `omlx/engine_core.py` routing logic.
* **Exit Criteria**: Existing AR tests pass using the new routing path.

## Phase 8: Streaming MoE

### Checkpoint 8.1: Python MoE Implementation
* **Goal**: Implement Streaming MoE execution in pure Python/MLX.
* **Purpose**: Prove the architecture works before optimizing.
* **Allowed Files**: `omlx/models/streaming_moe.py`, `tests/test_moe.py`.
* **Forbidden Files**: `omlx/custom_kernels/`, `omlx/scheduler.py`.
* **Dependencies**: Phase 3 (Execution Programs routing).
* **Verification**: Run `pytest tests/test_moe.py`.
* **Rollback Strategy**: Revert branch.
* **Exit Criteria**: Model runs successfully, albeit slowly.

## Phase 9: Optimization

### Checkpoint 9.1: Metal Kernels for MoE
* **Goal**: Push proven MoE bottlenecks into C++.
* **Purpose**: Optimize MoE inference speed.
* **Allowed Files**: `omlx/custom_kernels/streaming_moe/`, `omlx/models/streaming_moe.py`.
* **Forbidden Files**: `omlx/scheduler.py`, `omlx/engine_core.py`.
* **Dependencies**: Checkpoint 8.1 (Python implementation proven).
* **Verification**: Run `tests/test_hardware_benchmark.py` and unit tests to ensure parity.
* **Rollback Strategy**: Fallback to pure Python implementation.
* **Exit Criteria**: C++ kernel compiles and yields identical results to the Python implementation (Checkpoint 8.1) but faster.
