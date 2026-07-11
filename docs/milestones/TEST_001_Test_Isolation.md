# Milestone Plan — TEST-001: Test Isolation

This milestone outlines the strategy to resolve the cross-test state contamination in the `pytest` suite. Resolving this technical debt ensures that the entire test suite can be run successfully in a single invocation.

---

## 1. Architectural Goal
Eliminate cross-test dependencies and singleton state leakage resulting from global patches, mock registries, and cached modules in `sys.modules`.

---

## 2. Root Cause Analysis
- **Module Singletons**: Python caches imported modules in `sys.modules`. When test files patch or mutate these modules (e.g. `mlx_lm` models or core scheduler parameters), the mutation leaks to all subsequent tests run in the same process.
- **Global Mocking**: Standard tests use `monkeypatch` globally or write mocks to core components (like the model registry or engine pool) without restoring original states during teardown.
- **Shared Allocators**: Tests loading real/mock MLX weights alter the shared global Metal allocator caches and KV block buffers, affecting size checks in downstream test assertions.

---

## 3. Proposed Strategy & Tasks

### Task 3.1: Clean Mock Fixtures
- Replace direct imports patching with localized pytest `monkeypatch` or `unittest.mock` context managers.
- Audit all mock classes and ensure they are reset during fixture teardown.

### Task 3.2: Module Global State Reset
- Implement a setup/teardown fixture that clears and reloads target `omlx` submodules from `sys.modules` if they were patched.
- Ensure that the `settings` registry is cleanly re-initialized or reset to defaults before and after each test case.

### Task 3.3: Allocator and KV Cache Reset
- Introduce a fixture that calls `mlx.core.metal.clear_cache()` and frees KV cache structures globally on test teardown.

### Task 3.4: Process-Level Isolation
- Configure process-isolated execution runners (such as separate test groups or a subprocess invocation harness) to run state-heavy tests (e.g., VLM loaders and patches) in clean processes.

---

## 4. Definition of Done
- **Entire suite passes in one invocation**: Running `pytest` runs all tests sequentially with zero failures.
- **Entire suite passes with randomized order**: Using `pytest-randomly` or similar ordering plugins passes 100% cleanly.
- **Entire suite passes with pytest-xdist**: Running tests concurrently in separate worker processes results in zero test contamination.
- **No test modifies global runtime state without cleanup**: All global mutations (like patching standard libraries, or mutating shared attributes) are restored on teardown.
- **All monkeypatches are fixture scoped**: Direct global class assignments are replaced with fixture-scoped monkeypatches that automatically revert on exit.
- **No singleton survives between tests**: Any cached/singleton instances (such as configuration managers or engine pools) are explicitly cleared or re-instantiated.
- **No module import side effects affect later tests**: Submodules containing auto-registering side effects or global patches are reloaded dynamically or isolated.
