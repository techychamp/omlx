# oMLX Project Constitution

This file is the operating contract for working in this repository. It is derived from the codebase itself and should be treated as the local source of truth for future changes.

## 1. What This Repository Is

oMLX is a macOS-first local inference system built around MLX and `mlx-lm`, with a FastAPI server, a managed CLI, an admin surface, and a native SwiftUI app. The primary runtime path is:

`omlx/cli.py` -> `omlx/settings.py` -> `omlx/server.py` -> `omlx/engine_pool.py` -> `omlx/scheduler.py`

The repository also contains packaging and release machinery for the Swift app under `apps/omlx-mac/`, plus a venvstacks export pipeline in `packaging/`.

## 2. Source of Truth Hierarchy

When behavior appears in more than one place, prefer the following order:

1. Executable code in `omlx/`
2. Repo tests in `tests/`
3. The root `README.md`
4. Packaging and release docs under `packaging/` and `Formula/`
5. Platform app sources under `apps/omlx-mac/`

Do not introduce behavior that contradicts this order unless the change explicitly updates the whole chain.

## 3. Stable Runtime Ownership

The following modules own the core behavior of the product and should be changed carefully:

- `omlx/cli.py` owns command-line entry points, service lifecycle, and persisted CLI overrides.
- `omlx/settings.py` owns configuration loading, validation, directory setup, and scheduler config translation.
- `omlx/server.py` owns the FastAPI app, lifespan, auth checks, error handling, and route registration.
- `omlx/engine_pool.py` owns model discovery, load/unload decisions, LRU eviction, memory ceilings, and engine resolution.
- `omlx/scheduler.py` owns continuous batching, request scheduling, prefill handling, and generation coordination.
- `omlx/model_settings.py` owns per-model settings, aliases, TTL, pinned state, and exposed profile resolution.
- `omlx/model_discovery.py` owns filesystem-based model classification and discovery.
- `omlx/model_registry.py` owns cache ownership coordination and cleanup.
- `omlx/api/mcp_routes.py` owns the HTTP layer for MCP tool/server execution.

If a change affects more than one of these modules, update the tests that describe the boundary between them.

## 4. Experimental And Extension Seams

These areas exist, but they are not the default product contract and should be treated as extension points or experimental surfaces:

- `omlx/runtime/capabilities.py`
- `omlx/registry/plugin_discovery.py`
- `omlx/inference/execution_backend.py`
- `omlx/inference/execution_graph.py`
- `omlx/inference/modes.py`
- `omlx/inference/backends/experimental_diffusion_backend.py`

Rules for these surfaces:

1. Preserve the stable default path for normal LLM/VLM/embedding/reranker flows.
2. Keep experimental backends opt-in and clearly named.
3. Do not widen experimental behavior into the default path without a corresponding test update.
4. Treat plugin discovery and capability negotiation as contract surfaces, not internal helpers.

## 5. Packaging And Release Contract

Packaging is split between Python runtime export and the native macOS bundle:

- `packaging/build.py` produces the Python layers exported into the app bundle.
- `packaging/README.md` documents that the Swift app under `apps/omlx-mac/` is the only macOS bundle.
- `apps/omlx-mac/Scripts/build.sh` owns the actual `.app` build.
- `Formula/omlx.rb` governs Homebrew release behavior.

Rules:

1. Do not resurrect retired packaging paths unless the repo explicitly reintroduces them.
2. Keep the Swift app and Python backend packaging behavior consistent.
3. If release behavior changes, update the packaging docs and formula expectations together.

## 6. Testing Matrix

Pytest is the authoritative validation layer for the Python codebase. The existing tests cover the main behavior boundaries for CLI, server, scheduler, engine pool, settings, model discovery, registry, MCP routes, benchmarks, and experimental diffusion behavior.

Markers in `pytest.ini` matter:

- `slow`
- `integration`
- `turboquant`

What this means in practice:

1. Core runtime changes need unit coverage near the touched module.
2. Cross-module changes need an integration-style test where the boundary is observable.
3. Experimental backend changes must preserve the guardrails in the diffusion tests.
4. Performance and benchmark changes must not regress benchmark semantics.

## 7. Change Workflow

Before changing code, anchor the work in the smallest module that actually controls the behavior.

1. Start from the relevant runtime owner, not the most convenient wrapper.
2. Prefer an existing nearby test over inventing a new testing pattern.
3. Keep edits narrow and reversible.
4. If a change crosses stable and experimental surfaces, split it into explicit steps.
5. Update or add tests before claiming the behavior is done.

## 8. Validation Expectations

Use the cheapest executable check that can falsify the change first, then widen only if needed.

Typical validation choices for this repo:

- Targeted pytest module for the touched subsystem
- Narrow integration or boundary test for cross-module changes
- Repository test subset for CLI/server/settings regressions
- Benchmark-specific test for benchmark orchestration changes

Avoid claiming success on the basis of inspection alone when a test exists for the behavior.

## 9. Design Constraints To Preserve

The codebase already encodes these constraints and future edits should preserve them:

1. Settings are layered: environment, CLI, and persisted configuration all matter.
2. Engine admission is bounded by memory ceilings and eviction policy.
3. Model identity can be physical or profile-based; exposed profiles must resolve back to the owning model.
4. Registry ownership prevents conflicting cache ownership across engines.
5. Diffusion support is real, but it is still a special-case backend path.
6. The macOS app is the user-facing shell, while the Python server remains the core inference runtime.

## 10. What Not To Do

1. Do not add placeholder documents or generic boilerplate as a substitute for repository evidence.
2. Do not modify unrelated code while working on a narrow behavior change.
3. Do not flatten experimental surfaces into the stable runtime contract without tests.
4. Do not assume the Swift app, the Python server, and the packaging pipeline are interchangeable.
5. Do not introduce new abstractions unless the repository already shows a repeated need for them.

## 11. Canonical Evidence Map

If you need to re-derive the constitution from the code, start here:

- CLI and lifecycle: `omlx/cli.py`
- Server and routes: `omlx/server.py`
- Configuration and persistence: `omlx/settings.py`
- Scheduling and batching: `omlx/scheduler.py`
- Engine ownership and eviction: `omlx/engine_pool.py`
- Model discovery and classification: `omlx/model_discovery.py`
- Model profile state: `omlx/model_settings.py`
- Cache ownership registry: `omlx/model_registry.py`
- MCP transport: `omlx/api/mcp_routes.py`
- Experimental execution surfaces: `omlx/runtime/capabilities.py`, `omlx/inference/`
- Native app: `apps/omlx-mac/`
- Packaging and release: `packaging/`, `Formula/omlx.rb`

This file should be updated whenever the repo’s real ownership model changes.

## 12. Engineering Checkpoints

Every non-trivial change must be implemented as one checkpoint.

A checkpoint:

1. Has one architectural goal.
2. Modifies only closely related files.
3. Has explicit verification.
4. Can be reverted independently.
5. Produces an implementation report.

No checkpoint may begin until the previous checkpoint has passed verification.

## 13. Repository-Aware Planning

Every implementation must begin with repository analysis.

Required flow:

Repository Analysis -> Impact Analysis -> Implementation Plan -> Review -> Implementation -> Verification -> Checkpoint Complete

Implementation should follow the repository evidence first, then the plan, then the code.

## 14. Architecture Invariants

These are laws for the stable runtime:

1. Scheduler never performs inference.
2. Strategies coordinate execution.
3. ExecutionBackend owns execution selection and orchestration.
4. ExecutionEngine owns compute.
5. Capability negotiation decides execution mode.
6. Execution algorithms must not require Scheduler modifications.

If a checkpoint violates an invariant, stop and return for architectural review.

## 15. Verification Requirements

Every checkpoint must provide:

- Tests executed
- Files changed
- Files intentionally untouched
- Architecture impact
- Regression impact
- Evidence
- Confidence
- Known limitations

Do not mark work done without this evidence.

## 16. Definition Of Done

Done means:

- Code implemented
- Tests passing
- Architecture unchanged unless intentionally updated
- Documentation updated
- No dead code
- No TODO placeholders
- Checkpoint report written

## 17. Stop Conditions

Stop immediately and return for architectural review if any of these occur:

1. Scheduler redesign is required.
2. Public API changes unexpectedly.
3. More than 5 unrelated modules require modification.
4. Existing architecture becomes invalid.
5. Tests expose an architectural contradiction.

Do not continue past a stop condition.

## 18. Experimental Runtime Rules

Experimental features, including Nemotron diffusion and other capability-driven experimental paths, must:

1. Remain isolated.
2. Remain capability driven.
3. Remain opt-in.
4. Never change the default runtime path.

Experimental work should be validated against the dedicated experimental tests before it touches stable behavior.

## 19. Future Compatibility

Every new execution mode must integrate through:

ExecutionContext -> Capability Negotiation -> ExecutionProfile -> ExecutionBackend -> ExecutionPipeline

Never modify Scheduler to support a new model family.

If a new runtime path needs scheduler awareness, that is an architectural exception and must be reviewed explicitly.

## 20. AI Deliverables

Every AI agent working in this repository must return:

- Summary
- Architecture impact
- Files changed
- Verification evidence
- Risks
- Remaining work
- Recommendation
- Confidence

No exceptions.