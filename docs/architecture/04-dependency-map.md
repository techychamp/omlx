# Dependency Graph

## Major Packages & Modules
* **`omlx.api`**: FastAPI endpoints, depends on `omlx.engine_pool`, `omlx.models`, `omlx.mcp`.
* **`omlx.engine`**: Inference engine wrappers, depends on `omlx.inference`, `omlx.scheduler`, `omlx.cache`.
* **`omlx.inference`**: Generation algorithms, depends on `omlx.models`, `mlx_lm` (external).
* **`omlx.scheduler`**: Request batching, depends on `omlx.cache`.
* **`omlx.cache`**: Paged memory, SSD caching, depends on `mlx.core` (external).
* **`omlx.models`**: Model loading and patching, depends on `mlx_lm`.
* **`omlx.patches`**: Runtime monkey-patches for specific MLX logic, depends on `mlx_lm`.
* **`omlx.mcp`**: Model Context Protocol, depends on `omlx.api`.

## External Runtime Dependencies
* `mlx` & `mlx-lm`: Core tensor computation and standard model definitions.
* `fastapi` & `uvicorn`: API server and HTTP handling.
* `transformers`: Tokenization and configuration parsing.

## Initialization Order
1. `omlx.cli` (entry)
2. `omlx.config` / `omlx.settings`
3. `omlx.logging_config`
4. `omlx.registry.plugin_discovery`
5. `omlx.server` (starts API)
6. `omlx.engine_pool`
7. `omlx.model_discovery`
8. `omlx.engine_core` (lazy on request)

## Shutdown Order
1. HTTP Server stops accepting requests.
2. `omlx.engine_pool` evicts active leases.
3. `omlx.scheduler` clears pending requests.
4. `omlx.cache` commits to SSD (if applicable) and clears MLX cache.
5. Exit.

## Circular Dependencies
* None explicitly defined by architecture. Interfaces are mostly strictly layered (API -> Pool -> Engine -> Scheduler -> Cache -> MLX).
* `omlx.server` and `omlx.api.*` routes loosely couple via `ServerState` dependency injection.

## Interfaces
* **Stable Interfaces**: `EngineCore` API (`generate`, `abort`), `Scheduler` API (`add_request`, `step`), FastAPI endpoints.
* **Internal Interfaces**: `ExecutionGraph` nodes, `Cache` block allocators.
* **Experimental Interfaces**: Experimental diffusion backends (`omlx/inference/backends/experimental_diffusion_backend.py`), MoE extensions.
