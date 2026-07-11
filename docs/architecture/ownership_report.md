# Execution Architecture Discovery & Ownership Report

## 1. Component Implementations

### ExecutionBackend
*   **AutoregressiveBackend** ([autoregressive_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/backends/autoregressive_backend.py)): Execution backend for standard autoregressive models. Currently delegates to MLX-LM's `BatchGenerator`.
*   **ExperimentalNemotronBackend** ([experimental_diffusion_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/backends/experimental_diffusion_backend.py)): Execution backend that manages the Nemotron-Labs-Diffusion-3B model.
*   **FakeBackend** ([test_backend_compatibility.py](file:///Users/yugeshk/dev/repo/omlx/tests/test_backend_compatibility.py)): Test mock implementation of `ExecutionBackend`.

### ExecutionPipeline
*   **ExecutionPipeline** ([execution_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/execution_backend.py)): Base execution pipeline class that executes stages sequentially.
*   **AutoregressivePipeline** ([autoregressive_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/backends/autoregressive_backend.py)): Autoregressive pipeline executing `PrefillStage`, `ForwardStage`, `SampleStage`, `ExtractCacheStage`, and `EmitStage`.
*   **NemotronDiffusionPipeline** ([experimental_diffusion_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/backends/experimental_diffusion_backend.py)): Execution pipeline for Nemotron diffusion stages.
*   **FakePipeline** ([test_backend_compatibility.py](file:///Users/yugeshk/dev/repo/omlx/tests/test_backend_compatibility.py)): Test mock implementation of `ExecutionPipeline`.

### ExecutionEngine
*   **ExecutionEngine** Protocol ([execution_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/execution_backend.py)): Base protocol.
*   **AutoregressiveExecutionEngine** ([autoregressive_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/backends/autoregressive_backend.py)): Engine that wraps `BatchGenerator`.
*   **NemotronExecutionEngine** ([experimental_diffusion_backend.py](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/backends/experimental_diffusion_backend.py)): Engine that wraps `NemotronModelAdapter` and manages diffusion step operations.
*   **FakeEngine** ([test_backend_compatibility.py](file:///Users/yugeshk/dev/repo/omlx/tests/test_backend_compatibility.py)): Test mock implementation of `ExecutionEngine`.

---

## 2. Call Sites of Core Operations

### BatchGenerator
*   **Instantiations**:
    *   `omlx/scheduler.py` (Line 2556): Instantiated in `_create_batch_generator()`.
*   **Direct References / Attributes**:
    *   `omlx/scheduler.py`:
        *   `self.batch_generator: BatchGenerator | None = None`
        *   `self._ensure_batch_generator()` / `self.batch_generator = self._create_batch_generator(sampling_params)`
    *   `omlx/inference/backends/autoregressive_backend.py`:
        *   `class AutoregressiveExecutionEngine`: holds `self.batch_generator` property.
    *   `omlx/inference/execution_profile.py`:
        *   `_autoregressive_factory()`: instantiates `AutoregressiveExecutionEngine` with `batch_generator=None`.

### next_generated()
*   `omlx/scheduler.py` (Line 9261): `responses = list(self.batch_generator.next_generated())`
*   `omlx/inference/strategies/autoregressive.py` (Line 83): `return bg.next_generated()`
*   `omlx/inference/backends/autoregressive_backend.py` (Line 59): `return next(batch_generator.next_generated())`

### insert()
*   `omlx/scheduler.py` (Line 4164): `uids = self.batch_generator.insert(...)` (chunked prefill path)
*   `omlx/scheduler.py` (Line 8191): `uids = self.batch_generator.insert(...)` (standard prefill path)

### remove()
*   `omlx/scheduler.py` (Line 6708): `self.batch_generator.remove([uid])` (called inside `_remove_uid_from_active_batch()`)

### extract_cache()
*   `omlx/scheduler.py` (Line 4988): `result = self.batch_generator.extract_cache([uid])` (called inside `_get_boundary_decode_cache_snapshot()`)

---

## 3. Remaining Scheduler → BatchGenerator Coupling

Currently, `Scheduler` directly:
1. Controls the instantiation, lifecycle, and destruction of `self.batch_generator`.
2. Directly runs `.insert()`, `.remove()`, `.extract_cache()`, and `.next_generated()`.
3. Directly queries/accesses internal properties of the `BatchGenerator` (e.g. `_generation_batch.prompt_cache` inside `_eval_generation_batch_cache`).
4. Checks if `self.batch_generator is None` to guide runtime and state assertions.

All of these represent direct coupling between the Scheduler and `BatchGenerator`, violating the target architecture where the `BatchGenerator` is a private implementation detail of the `ExecutionEngine`.
