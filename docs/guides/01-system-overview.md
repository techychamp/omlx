# OMLX System Overview

## Runtime Architecture Execution Trace

The execution flow of OMLX from entry point to major components operates as follows:

1. **CLI Entry Point (`omlx/cli.py`)**: The application is launched via the CLI. The `serve` command is the primary entry point for starting the inference server.
2. **Server Initialization (`omlx/server.py`)**: The CLI instantiates the server. The `ServerState` holds global state.
3. **Engine Management (`omlx/engine_pool.py`)**: The server initializes an `EnginePool`. The pool manages leases for different inference engines (e.g., `EngineType.LLM`, `EngineType.VLM`).
4. **Engine Core (`omlx/engine_core.py`)**: For LLM/VLM generation, an `EngineCore` is instantiated. This core wraps the `mlx-lm` backend and provides continuous batching capabilities.
5. **Scheduler (`omlx/scheduler.py`)**: The `EngineCore` delegates the complex task of continuous batching to the `Scheduler`. The scheduler manages the queue of requests, implementing policies like First-Come-First-Serve (FCFS). It handles memory bounds, prefill chunking, and delegates to the `mlx-lm` `BatchGenerator` for the actual forward passes.
6. **Execution Graph & Inference (`omlx/inference/`)**: During execution, strategies define how inference operates. Execution graphs (`omlx/inference/execution_graph.py`) abstract node types like PREFILL, FORWARD, SAMPLE, and DENOISE.
7. **Cache (`omlx/cache/`)**: State across inference requests is handled by the cache subsystem (e.g., `paged_ssd_cache.py`, `hybrid_cache.py`), integrated tightly with the scheduling step.
