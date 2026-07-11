# oMLX Technical Debt Register: Checkpoint a46ab94

This document tracks technical debt introduced or remaining in the oMLX local inference runtime after the implementation of checkpoint `a46ab94` ("added foundation for triage & updated scheduler").

---

## 1. Newly Introduced Technical Debt

### A. Non-Defensive Attribute Resolution in Scheduler
The scheduler's prefill chunk and decode steps query `self.strategy` directly:
```python
if self.strategy is not None:
```
- **Rationale**: Assumes the target object is a fully initialized `Scheduler` instance.
- **Risk**: Fails with `AttributeError` when interacting with mock schedulers or light wrappers (e.g. `types.SimpleNamespace` in `test_prefill_oom_graceful.py`) that lack a default `strategy` property.
- **Remediation**: Use `getattr(self, "strategy", None)` to resolve the property safely.

### B. Catch-All Exception Block in `EngineCore`
During `EngineCore` initialization, the strategy resolution pipeline is wrapped in a broad try/except block ([engine_core.py:L262-317](file:///Users/yugeshk/dev/repo/omlx/omlx/engine_core.py#L262-317)):
```python
try:
    # 1. Infer model capabilities...
    # 2. Build model info...
    # ...
    self.scheduler.set_strategy(strategy)
except Exception as e:
    logger.warning(
        f"Failed to independently resolve execution strategy during EngineCore initialization: {e}. "
        "Continuing without a bound strategy."
    )
```
- **Rationale**: This is a defensive fallback mechanism. If capability resolution fails, the engine continues to run using the default (legacy) autoregressive path inside the scheduler.
- **Risk**: A catch-all exception swallows legitimate bugs during development, such as typos, import errors, or initialization mismatches in capability resolution or registries, reducing debuggability.
- **Remediation**:
  - Log the full stack trace when `LOG_LEVEL` is set to `DEBUG`.
  - Let exceptions bubble up in test environments (`pytest`) to capture regressions immediately, rather than fallback.

### C. Inline Imports in `BaseGenerationStrategy`
Inside `BaseGenerationStrategy.prefill` ([strategy.py:L67](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/strategy.py#L67)):
```python
def prefill(self, model: Any, inputs: Any, cache: Any, **kwargs: Any) -> None:
    import mlx.core as mx
    model(inputs, cache=cache, **kwargs)
    mx.eval([c.state for c in cache])
```
- **Rationale**: Avoids module-level imports of `mlx.core` in abstract strategy files that might be imported in environments where `mlx` is not loaded.
- **Risk**: Minor clean-code smell. Duplicated inline imports of `mlx` across execution layers.

### D. Redundant Scheduler Execution Paths
The `Scheduler` contains duplicated fallback branches for prefill and decode:
- **Prefill**:
  ```python
  if self.strategy is not None:
      self.strategy.prefill(self.model, input_arr[:, :n_to_process], cache=prompt_cache, **model_kwargs)
  else:
      self.model(input_arr[:, :n_to_process], cache=prompt_cache, **model_kwargs)
      mx.eval([c.state for c in prompt_cache])
  ```
- **Decode**:
  ```python
  if self.strategy is not None:
      responses = list(self.strategy.forward())
  else:
      responses = list(self.batch_generator.next_generated())
  ```
- **Risk**: Increases code size and testing surface. If logic shifts, both branches must be updated or tested.
- **Remediation**: Once the strategy delegation has proven stable, remove the fallback branches and make strategy binding mandatory (e.g., defaulting to `AutoregressiveStrategy`).

---

## 2. Legacy Technical Debt Remaining

### A. Hardcoded Speculative Decoding in Scheduler
- **File**: [scheduler.py](file:///Users/yugeshk/dev/repo/omlx/omlx/scheduler.py)
- **Code**: `self._vlm_mtp_active` and `_step_vlm_mtp()` are still hardcoded directly inside the scheduler's decode step loop ([scheduler.py:L9267](file:///Users/yugeshk/dev/repo/omlx/omlx/scheduler.py#L9267)).
- **Impact**: Violates the "Scheduler never performs inference" invariant because speculative decoding is coordinated inside `scheduler.py` instead of a speculative strategy class.
- **Remediation**: Migrate VLM MTP and Speculative Prefill logic to a custom `SpeculativeStrategy` class under `omlx/inference/strategies/`.

### B. Hardcoded Model-Name Coupling
- **File**: [scheduler.py:L1627](file:///Users/yugeshk/dev/repo/omlx/omlx/scheduler.py#L1627)
- **Code**:
  ```python
  model_name_lower = (self.config.model_name or "").lower()
  default_kv_eval_interval = 256 if "minimax" in model_name_lower else 0
  ```
- **Impact**: Couples the core scheduler class to specific commercial model names ("minimax").
- **Remediation**: Move the custom KV evaluation interval requirement into the `ExecutionProfile` resolved during capability negotiation.
