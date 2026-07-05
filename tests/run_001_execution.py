#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
RUN-001 — First Real Compiler-Driven Model Execution
=====================================================

Self-contained execution harness for RUN-001 milestone.

Phase A — Compiler Pipeline Validation
    Drives the full compiler runtime:
    RuntimeCompilerService → CapabilityResolver → ExecutionPlanner → IRBuilder →
    LoweringEngine → MLXAdapter.translate() → BackendOperationGraph →
    ExecutionEngine → SequentialExecutionDispatcher → MLXAdapter.execute()

Phase B — Real Model Inference (Compatibility Shim)
    Loads TinyLlama-1.1B-Chat-v1.0-4bit via mlx_lm.utils.load() and calls
    mlx_lm.generate() directly. This shim lives in the harness, NOT inside
    the backend adapter, preserving the architectural separation for BACKEND-005.

Phase C — Artifact Bundle
    Writes all compiler artifacts and inference results to run_artifacts/.

Usage:
    python tests/run_001_execution.py

Environment variables:
    OMLX_RUN001_MODEL        Override model ID (default: mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit)
    OMLX_RUN001_PROMPT       Override prompt text
    OMLX_RUN001_MAX_TOKENS   Override max_tokens (default: 10)
    OMLX_RUN001_ARTIFACTS_DIR Override artifact output directory (default: run_artifacts)
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("omlx.run_001")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MODEL_ID = os.environ.get(
    "OMLX_RUN001_MODEL",
    "mlx-community/TinyLlama-1.1B-Chat-v1.0-4bit",
)
PROMPT = os.environ.get("OMLX_RUN001_PROMPT", "The capital of France is")
MAX_TOKENS = int(os.environ.get("OMLX_RUN001_MAX_TOKENS", "10"))
TEMPERATURE = 0.0  # deterministic
ARTIFACTS_DIR = Path(
    os.environ.get("OMLX_RUN001_ARTIFACTS_DIR", "run_artifacts")
)


# ---------------------------------------------------------------------------
# Helper: JSON-safe serialiser
# ---------------------------------------------------------------------------

def _to_json(obj: Any, indent: int = 2) -> str:
    """Convert arbitrary objects to a JSON-safe representation."""
    def _cvt(o: Any) -> Any:
        if isinstance(o, (str, int, float, bool, type(None))):
            return o
        if isinstance(o, (MappingProxyType, dict)):
            return {str(k): _cvt(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_cvt(i) for i in o]
        if hasattr(o, "__dataclass_fields__"):
            result = {}
            for f_name in o.__dataclass_fields__:
                try:
                    result[f_name] = _cvt(getattr(o, f_name))
                except Exception:
                    result[f_name] = repr(getattr(o, f_name))
            return result
        if hasattr(o, "value"):  # Enum
            return o.value
        return repr(o)
    return json.dumps(_cvt(obj), indent=indent)


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

@dataclass
class PhaseAResult:
    """Result of Phase A — Compiler Pipeline Validation."""
    success: bool = False
    error: Optional[str] = None
    capability_descriptor: Any = None
    execution_plan: Any = None
    logical_ir: Any = None
    physical_ir: Any = None
    backend_operation_graph: Any = None
    translation_result: Any = None
    compiler_session: Any = None
    compiler_statistics: Any = None
    execution_result: Any = None
    execution_statistics: Any = None
    execution_schedule_diagnostics: Any = None
    pipeline_duration_ms: float = 0.0
    engine_duration_ms: float = 0.0


@dataclass
class PhaseBResult:
    """Result of Phase B — Real Model Inference."""
    success: bool = False
    error: Optional[str] = None
    model_id: str = ""
    prompt: str = ""
    generated_text: str = ""
    token_count: int = 0
    load_duration_ms: float = 0.0
    inference_duration_ms: float = 0.0


# ---------------------------------------------------------------------------
# Phase A — Compiler Pipeline Validation
# ---------------------------------------------------------------------------

def run_phase_a(model_label: str, model: "Any" = None, tokenizer: "Any" = None) -> PhaseAResult:
    """
    Drive the full compiler pipeline for model_label, then execute the
    resulting BackendOperationGraph through the ExecutionEngine.

    MLXAdapter.execute() returns its structural mock response per operation
    — correct by design. Phase A validates the compiler pipeline architecture.
    """
    result = PhaseAResult()
    logger.info("=" * 60)
    logger.info("PHASE A — Compiler Pipeline Validation")
    logger.info("  model_label : %s", model_label)
    logger.info("=" * 60)

    try:
        from omlx.runtime.feature_flags import FeatureFlags
        from omlx.runtime.builder import RuntimeBuilder
        from omlx.runtime.execution import ExecutionContext, ExecutionStatus

        flags = FeatureFlags(
            COMPILER_RUNTIME_PIPELINE_ENABLED=True,
            COMPILER_RUNTIME_ENABLED=True,
            COMPILER_CONTEXT_ENABLED=True,
            CAPABILITY_RUNTIME_ENABLED=True,
            PLANNER_RUNTIME_ENABLED=True,
            LOWERING_RUNTIME_ENABLED=True,
            ADAPTER_RUNTIME_ENABLED=True,
        )

        logger.info("[A1] Building Runtime with full compiler flags ...")
        runtime = RuntimeBuilder().with_feature_flags(flags).build()
        logger.info("     Runtime state: %s", runtime.state)

        logger.info("[A2] Running RuntimeCompilerService.run_compilation('%s') ...", model_label)
        pipeline_start = time.perf_counter()
        translation_result = runtime.compiler_service.run_compilation(model_label)
        result.pipeline_duration_ms = (time.perf_counter() - pipeline_start) * 1000

        if translation_result is None:
            result.error = "Compiler pipeline returned None"
            logger.error("[A2] FAILED: %s", result.error)
            return result

        logger.info("     Pipeline completed in %.2f ms", result.pipeline_duration_ms)
        result.translation_result = translation_result

        ctx = runtime.context
        result.capability_descriptor = ctx.capability_descriptor
        result.execution_plan = ctx.execution_plan
        result.logical_ir = ctx.logical_ir
        result.physical_ir = ctx.physical_ir
        result.backend_operation_graph = ctx.backend_operation_graph
        result.compiler_session = ctx.compiler_session
        result.compiler_statistics = runtime.compiler_service.statistics

        bg = translation_result.backend_graph
        logger.info("[A3] BackendOperationGraph:")
        logger.info("     backend_id : %s", bg.backend_id)
        logger.info("     operations : %s", list(bg.operations.keys()))
        logger.info("     roots      : %s", bg.roots)

        logger.info("[A4] Resolving MLXAdapter ...")
        adapter = runtime.adapter_registry.resolve(
            backend="mlx", hardware="any",
            execution_family="autoregressive", execution_mode="streaming",
        )
        logger.info("     Adapter: %s", adapter.__class__.__name__)

        exec_ctx = ExecutionContext(
            request_context=None,
            backend_operation_graph=bg,
            adapter=adapter,
        )

        logger.info("[A5] ExecutionEngine.execute() ...")
        engine_start = time.perf_counter()
        exec_result = runtime.execution_engine.execute(exec_ctx)
        result.engine_duration_ms = (time.perf_counter() - engine_start) * 1000

        result.execution_result = exec_result
        result.execution_statistics = exec_result.statistics
        result.execution_schedule_diagnostics = exec_result.diagnostics

        if exec_result.status == ExecutionStatus.COMPLETED:
            logger.info("     ExecutionEngine COMPLETED in %.3f ms", result.engine_duration_ms)
            logger.info("     Operations executed : %s",
                        exec_result.statistics.executed_operations if exec_result.statistics else "N/A")
            logger.info("     Adapter calls       : %s",
                        exec_result.statistics.adapter_calls if exec_result.statistics else "N/A")
            result.success = True
        else:
            result.error = f"ExecutionEngine returned status: {exec_result.status}"
            logger.error("[A5] FAILED: %s", result.error)

    except Exception as e:
        result.error = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        logger.error("[PHASE A] Exception:\n%s", result.error)

    return result


# ---------------------------------------------------------------------------
# Phase B — Real Model Inference (Compatibility Shim)
# ---------------------------------------------------------------------------

def run_phase_b(model_id: str, prompt: str, max_tokens: int, temperature: float) -> PhaseBResult:
    """
    Load TinyLlama via mlx_lm.utils.load() and call mlx_lm.generate() directly.
    This is the RUN-001 compatibility shim — mlx_lm.generate() lives here in the
    harness, NOT inside MLXAdapter.execute(). Architectural separation preserved.
    """
    result = PhaseBResult(model_id=model_id, prompt=prompt)
    logger.info("=" * 60)
    logger.info("PHASE B — Real Model Inference (Compatibility Shim)")
    logger.info("  model      : %s", model_id)
    logger.info("  prompt     : %r", prompt)
    logger.info("  max_tokens : %d", max_tokens)
    logger.info("  temperature: %.1f", temperature)
    logger.info("=" * 60)

    try:
        from mlx_lm.utils import load as mlx_load
        import mlx_lm
        from huggingface_hub import snapshot_download
        import glob
        import pathlib

        # Resolve the local cached snapshot path first. mlx_lm._download() uses
        # allow_patterns=["model*.safetensors"] which filters out mlx-community's
        # weights.00.safetensors naming convention. By resolving to the local
        # snapshot directory and passing it directly, we bypass the pattern filter.
        logger.info("[B1] Resolving local cache path for '%s' ...", model_id)
        local_snap = pathlib.Path(snapshot_download(model_id, local_files_only=True))
        logger.info("     Snapshot: %s", local_snap)

        # Ensure mlx_lm can find the weights: it globs "model*.safetensors".
        # If the cached file uses a different name (e.g. weights.00.safetensors),
        # create a compatible symlink inside the snapshot so mlx_lm finds it.
        existing_model = glob.glob(str(local_snap / "model*.safetensors"))
        if not existing_model:
            other_safetensors = glob.glob(str(local_snap / "*.safetensors"))
            if other_safetensors:
                target_blob = pathlib.Path(other_safetensors[0]).resolve()
                compat_link = local_snap / "model.safetensors"
                if not compat_link.exists():
                    import os
                    os.symlink(target_blob, compat_link)
                    logger.info("     Created model.safetensors compat symlink → %s", target_blob.name)
                else:
                    logger.info("     model.safetensors compat symlink already exists")
            else:
                raise FileNotFoundError(f"No safetensors files found in {local_snap}")

        logger.info("[B2] Loading model via mlx_lm.utils.load(local_path) ...")
        load_start = time.perf_counter()
        model, tokenizer = mlx_load(str(local_snap))
        result.load_duration_ms = (time.perf_counter() - load_start) * 1000
        logger.info("     Loaded in %.0f ms — model: %s  tokenizer: %s",
                    result.load_duration_ms, type(model).__name__, type(tokenizer).__name__)

        logger.info("[B3] Tokenizing prompt ...")
        token_ids = tokenizer.encode(prompt)
        logger.info("     Token IDs: %s (%d tokens)", token_ids, len(token_ids))

        logger.info("[B4] Calling mlx_lm.generate() ...")
        from mlx_lm.sample_utils import make_sampler
        # In mlx_lm 0.31.3+, temperature is passed via a sampler callable,
        # not as a direct kwarg. make_sampler(temp=0.0) produces greedy/argmax decoding.
        sampler = make_sampler(temp=temperature)
        inference_start = time.perf_counter()
        generated_text = mlx_lm.generate(
            model,
            tokenizer,
            prompt=prompt,
            verbose=False,
            max_tokens=max_tokens,
            sampler=sampler,
        )
        result.inference_duration_ms = (time.perf_counter() - inference_start) * 1000
        result.generated_text = generated_text
        result.token_count = len(tokenizer.encode(generated_text))

        logger.info("     Inference completed in %.0f ms", result.inference_duration_ms)
        logger.info("     Generated text : %r", generated_text)
        logger.info("     Token count    : %d", result.token_count)
        result.success = True

    except Exception as e:
        result.error = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        logger.error("[PHASE B] Exception:\n%s", result.error)

    return result


# ---------------------------------------------------------------------------
# Phase C — Artifact Bundle
# ---------------------------------------------------------------------------

def write_artifacts(
    phase_a: PhaseAResult,
    phase_b: PhaseBResult,
    artifacts_dir: Path,
    start_time: float,
) -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logger.info("=" * 60)
    logger.info("PHASE C — Writing Artifact Bundle to %s/", artifacts_dir)
    logger.info("=" * 60)

    def write(name: str, obj: Any) -> None:
        path = artifacts_dir / name
        try:
            path.write_text(_to_json(obj), encoding="utf-8")
            logger.info("  [C] %s", path.name)
        except Exception as e:
            logger.warning("  [C] Could not write %s: %s", path.name, e)

    write("model_descriptor.json", {
        "model_id": phase_b.model_id,
        "model_label_used_in_compiler": "TinyLlama-1.1B",
        "execution_family": "autoregressive",
        "backend": "mlx",
    })
    write("capability_descriptor.json", phase_a.capability_descriptor)
    write("execution_plan.json", phase_a.execution_plan)
    write("logical_ir.json", phase_a.logical_ir)
    write("physical_ir.json", phase_a.physical_ir)
    write("backend_operation_graph.json", phase_a.backend_operation_graph)
    write("translation_result.json", phase_a.translation_result)
    write("execution_schedule.json", phase_a.execution_schedule_diagnostics)
    write("statistics.json", phase_a.execution_statistics)
    write("diagnostics.json", {
        "phase_a_error": phase_a.error,
        "phase_b_error": phase_b.error,
        "execution_schedule_diagnostics": phase_a.execution_schedule_diagnostics,
    })
    write("compiler_session.json", phase_a.compiler_session)
    write("compiler_statistics.json", phase_a.compiler_statistics)
    write("runtime_context.json", {
        "capability_descriptor": phase_a.capability_descriptor,
        "execution_plan": phase_a.execution_plan,
        "backend_operation_graph": phase_a.backend_operation_graph,
        "compiler_statistics": phase_a.compiler_statistics,
    })
    write("execution_context.json", {
        "backend_operation_graph": phase_a.backend_operation_graph,
        "execution_statistics": phase_a.execution_statistics,
        "adapter": "MLXAdapter (structural — BACKEND-005 will implement real kernel dispatch)",
        "model": phase_b.model_id if phase_b.success else None,
        "tokenizer": "loaded" if phase_b.success else None,
    })

    # --- run_report.md ---
    total_s = time.time() - start_time
    a_ok = "PASSED" if phase_a.success else "FAILED"
    b_ok = "PASSED" if phase_b.success else "FAILED"

    lines = [
        "# RUN-001 — First Real Compiler-Driven Model Execution",
        "",
        "## Summary",
        "",
        "| Phase | Status | Duration |",
        "|---|---|---|",
        f"| Phase A — Compiler Pipeline | {a_ok} | {phase_a.pipeline_duration_ms:.2f} ms pipeline + {phase_a.engine_duration_ms:.3f} ms engine |",
        f"| Phase B — Real Inference    | {b_ok} | {phase_b.load_duration_ms:.0f} ms load + {phase_b.inference_duration_ms:.0f} ms inference |",
        f"| Total harness duration      | — | {total_s:.2f} s |",
        "",
    ]

    if phase_b.success:
        lines += [
            "## Generated Output",
            "",
            f"**Model:** `{phase_b.model_id}`  ",
            f"**Prompt:** `{phase_b.prompt}`  ",
            f"**Generated:** `{phase_b.generated_text}`  ",
            f"**Token count:** {phase_b.token_count}  ",
            f"**Temperature:** {TEMPERATURE} (deterministic)  ",
            "",
        ]

    lines += [
        "## Compiler Pipeline Walkthrough",
        "",
        "```",
        "Model ID  (TinyLlama-1.1B)",
        "  ↓",
        "CapabilityResolver.resolve()     → CapabilityDescriptor",
        "  ↓",
        "ExecutionPlanner.plan()          → ExecutionPlan",
        "  ↓",
        "IRBuilder.build()                → LogicalIR (ExecutionIR)",
        "  ↓",
        "LoweringEngine.lower()           → PhysicalIR",
        "  ↓",
        "MLXAdapter.translate()           → TranslationResult + BackendOperationGraph",
        "  ↓",
        "ExecutionEngine.execute()        → DeterministicGraphExecutor",
        "  ↓",
        "GraphScheduler.build_schedule()  → ExecutionSchedule",
        "  ↓",
        "SequentialExecutionDispatcher    → per-operation dispatch",
        "  ↓",
        "MLXAdapter.execute() × 5         → structural mock (BACKEND-005 pending)",
        "```",
        "",
        "## Phase A — Compiler Artifacts",
        "",
    ]

    cd = phase_a.capability_descriptor
    if cd is not None:
        lines += [
            "**CapabilityDescriptor**",
            f"- execution_family   : `{cd.execution_family}`",
            f"- supports_streaming : `{cd.supports_streaming}`",
            f"- attention_types    : `{cd.attention_types}`",
            "",
        ]

    ep = phase_a.execution_plan
    if ep is not None:
        lines += [
            "**ExecutionPlan**",
            f"- execution_family   : `{ep.execution_family}`",
            f"- execution_backend  : `{ep.execution_backend}`",
            f"- execution_mode     : `{ep.execution_mode}`",
            f"- scheduler_strategy : `{ep.scheduler_strategy}`",
            "",
        ]

    bg = phase_a.backend_operation_graph
    if bg is not None:
        lines += [
            "**BackendOperationGraph**",
            f"- backend_id  : `{bg.backend_id}`",
            f"- operations  : `{list(bg.operations.keys())}`",
            f"- roots       : `{bg.roots}`",
            "",
        ]

    st = phase_a.execution_statistics
    if st is not None:
        lines += [
            "**ExecutionStatistics**",
            f"- executed_operations       : `{st.executed_operations}`",
            f"- backend_invocations       : `{st.backend_invocations}`",
            f"- adapter_calls             : `{st.adapter_calls}`",
            f"- execution_duration_ms     : `{st.execution_duration_ms:.3f} ms`",
            f"- compiler_execution_count  : `{st.compiler_execution_count}`",
            f"- legacy_fallback_count     : `{st.legacy_fallback_count}`",
            "",
        ]

    lines += [
        "## Phase B — Real Inference Shim",
        "",
        "Phase B calls `mlx_lm.generate()` directly from the harness, **not** via",
        "`MLXAdapter.execute()`. This preserves the architectural boundary for BACKEND-005.",
        "",
        "## Known Limitations",
        "",
        "- `MLXAdapter.execute()` is a structural mock; real kernel dispatch is BACKEND-005.",
        "- Phase A compiler plan uses a synthetic model label (no weight loading in compiler).",
        "- Phase B inference (mlx_lm.generate) is a compatibility shim, not compiler-driven decode.",
        "",
        "## Recommendations",
        "",
        "- BACKEND-005: Implement real MLX forward kernel dispatch in `MLXAdapter.execute()`.",
        "- Bridge Phase A and Phase B by injecting the loaded model into `ExecutionContext.model`.",
        "- Add a streaming decode loop driven by the compiler's `ExecutionSchedule`.",
        "",
        "## Artifact Index",
        "",
        "| File | Contents |",
        "|---|---|",
        "| `model_descriptor.json` | Model identification record |",
        "| `capability_descriptor.json` | CapabilityDescriptor from resolver |",
        "| `execution_plan.json` | ExecutionPlan from planner |",
        "| `logical_ir.json` | LogicalIR from IRBuilder |",
        "| `physical_ir.json` | PhysicalIR from LoweringEngine |",
        "| `backend_operation_graph.json` | BackendOperationGraph from MLXAdapter |",
        "| `translation_result.json` | Full TranslationResult with diagnostics |",
        "| `execution_schedule.json` | ExecutionSchedule diagnostics |",
        "| `statistics.json` | ExecutionStatistics |",
        "| `diagnostics.json` | Error/diagnostic summary |",
        "| `compiler_session.json` | CompilerSession lifecycle record |",
        "| `compiler_statistics.json` | RuntimeCompilerService statistics |",
        "| `runtime_context.json` | Runtime context snapshot |",
        "| `execution_context.json` | ExecutionContext snapshot |",
        "| `run_report.md` | This report |",
    ]

    if phase_a.error:
        lines += ["", "## Phase A Error", "", "```", phase_a.error, "```"]
    if phase_b.error:
        lines += ["", "## Phase B Error", "", "```", phase_b.error, "```"]

    (artifacts_dir / "run_report.md").write_text("\n".join(lines), encoding="utf-8")
    logger.info("  [C] run_report.md")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    start_time = time.time()
    logger.info("RUN-001 — First Real Compiler-Driven Model Execution")
    logger.info("  model     : %s", MODEL_ID)
    logger.info("  prompt    : %r", PROMPT)
    logger.info("  max_tokens: %d", MAX_TOKENS)
    logger.info("  artifacts : %s/", ARTIFACTS_DIR)
    logger.info("")

    model, tokenizer = None, None
    try:
        from huggingface_hub import snapshot_download
        import glob
        import pathlib

        # We handle mock imports during CI vs local environment gracefully
        try:
            from mlx_lm.utils import load as mlx_load
        except ImportError:
            mlx_load = None

        if mlx_load:
            logger.info("Pre-loading model for ExecutionContext via mlx_lm...")
            local_path = snapshot_download(repo_id=MODEL_ID)
            model, tokenizer = mlx_load(local_path)
        else:
            logger.info("mlx_lm not available; bypassing pre-load for Phase A.")
    except Exception as e:
        logger.warning(f"Could not load real model: {e}")

    phase_a = run_phase_a(model_label="TinyLlama-1.1B", model=model, tokenizer=tokenizer)
    phase_b = run_phase_b(
        model_id=MODEL_ID,
        prompt=PROMPT,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    write_artifacts(phase_a, phase_b, ARTIFACTS_DIR, start_time)

    logger.info("")
    logger.info("=" * 60)
    logger.info("RUN-001 SUMMARY")
    logger.info("=" * 60)
    logger.info("  Phase A (compiler pipeline) : %s", "PASSED" if phase_a.success else "FAILED")
    logger.info("  Phase B (real inference)     : %s", "PASSED" if phase_b.success else "FAILED")
    if phase_b.success:
        logger.info("  Generated text              : %r", phase_b.generated_text)
    logger.info("  Artifacts at                : %s/", ARTIFACTS_DIR)
    logger.info("  Total duration              : %.2f s", time.time() - start_time)

    return 0 if (phase_a.success and phase_b.success) else 1


if __name__ == "__main__":
    sys.exit(main())
