# IMP-001 Feature Flag Infrastructure Report

## 1. Repository Audit Inventory

Based on an audit of the repository, the following existing environment variables act as feature toggles, limits, or configurations that are prime candidates for the new Feature Flag system in future checkpoints:

- **Engine Constraints / Features**:
  - `OMLX_DECODE_BURST_MAX_STEPS`
  - `OMLX_DECODE_BURST_BUDGET_SINGLE_S`
  - `OMLX_DECODE_BURST_BUDGET_S`
- **Experimental Code Paths / Patches**:
  - `MLX_LM_GLM_DSA_ADAPTIVE_PREFILL_STEP`
  - `MLX_LM_GLM_DSA_ADAPTIVE_PREFILL_STEP_SIZE`
  - `MLX_LM_GLM_DSA_ADAPTIVE_PREFILL_AFTER`
  - `MLX_LM_GLM_DSA_ADAPTIVE_PREFILL_MIN_REMAINING`
  - `MLX_MINIMAX_M3_ADAPTIVE_PREFILL_STEP`
  - `MLX_MINIMAX_M3_ADAPTIVE_PREFILL_STEP_SIZE`
  - `MLX_MINIMAX_M3_ADAPTIVE_PREFILL_AFTER`
  - `MLX_MINIMAX_M3_ADAPTIVE_PREFILL_MIN_REMAINING`
- **Compatibility Layers / Fallbacks**:
  - `_NATIVE_TOPK_SELECT_MODE` (in `mlx_vlm_minimax_m3_compat`)
  - `_NATIVE_MSA_TOPK_MODE`
- **General Configuration**:
  - `OMLX_BASE_PATH`
  - `OMLX_SUPERVISED`
  - `OMLX_SECRET_KEY`

These toggles currently bypass any formal lifecycle or centralized registry. The `feature_flags` subsystem provides the necessary infrastructure to deprecate this fragmented approach.

## 2. Architecture Impact

The new Feature Flag subsystem introduces a strictly separate concern in `omlx/feature_flags`.

**What changed**:
- Added `omlx/feature_flags/models.py` for strictly-typed flag definitions.
- Added `omlx/feature_flags/registry.py` for pre-boot registration.
- Added `omlx/feature_flags/resolver.py` for precedence-based evaluation (CLI > Env > Config > Default).
- Added `omlx/feature_flags/system.py` providing the `feature_flags_system` and `ImmutableSnapshot` pattern.
- Added `tests/test_feature_flags.py` containing 11 tests.

**What did NOT change**:
- The `Scheduler`, `ExecutionEngine`, `ModelAdapter`, and other core systems remain completely untouched.
- No existing feature toggles were migrated (in accordance with IMP-001 constraints).
- No new runtime behavior was activated.

## 3. Verification Evidence

A comprehensive test suite was added to `tests/test_feature_flags.py` and run successfully.

**Test Coverage**:
- Default resolution logic
- Environment variable overrides
- Configuration overrides
- CLI overrides
- Resolution precedence (CLI over Env over Config over Default)
- Pre-boot Immutability (Snapshot prevents mutations)
- Unknown flag detection
- Duplicate flag registration errors
- Type resolution (`INTEGER`, `BOOLEAN`, etc.)
- Export and Listing

**Results**: `11 passed in 0.32s`

## 4. Rollback Procedure

Because this system is entirely isolated and not yet invoked by `RuntimeBuilder` or any other part of the application, rollback requires simply deleting the `omlx/feature_flags` directory and `tests/test_feature_flags.py`.

## 5. Recommendations for IMP-002

During IMP-002 (RuntimeBuilder integration):
- Initialize `feature_flags_system` during the Boot Phase.
- Process CLI arguments and configuration files, injecting overrides via `set_cli_overrides` and `set_config_overrides`.
- Invoke `feature_flags_system.take_snapshot()` right before initializing the core dependencies (e.g., Engine, Scheduler) to seal the state.
- Pass the `ImmutableSnapshot` directly into dependencies that need feature flags, explicitly forbidding access to the global `feature_flags_system` post-boot.
