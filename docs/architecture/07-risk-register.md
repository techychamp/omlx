# Repository Risk Map & Technical Debt

## Risk Map

| Subsystem / Area | Risk Level | Reason | Protective Tests | Future Modifiers |
|---|---|---|---|---|
| **Scheduler** | 🟡 Medium Risk | Highly complex continuous batching logic; manages IOKit/Metal synchronization and prefill chunking. | `tests/test_scheduler*.py` | Dynamic Execution Planning |
| **Cache (SSD/Paged)** | 🟡 Medium Risk | Interacts directly with memory constraints. High statefulness. | `tests/test_paged_ssd_cache.py`, `tests/test_cache_*.py` | Streaming MoE, Nemotron |
| **EngineCore** | 🟢 Stable | Core generation loop is mature and well tested. | `tests/test_engine_core.py` | New Engine Types |
| **API Surface** | 🟢 Stable | Standard FastAPI/OpenAI abstractions. | `tests/test_api_*.py` | MCP Extensions |
| **Model Patches** | 🔴 Critical | `omlx.patches` rely on unstable upstream `mlx_lm` internals. High risk on MLX upgrades. | Specific patch tests (e.g. `test_glm_moe_dsa_patch.py`) | Any new model arch |
| **Memory Monitor** | 🟡 Medium Risk | System memory probing is OS dependent and subject to race conditions. | `tests/test_memory_monitor*.py` | |

## Technical Debt Register

### 1. `omlx.patches` Directory
* **Classification**: Critical
* **Why**: MLX/MLX-LM do not always expose required hooks for complex model topologies (e.g., Minimax, DeepSeek V4). We are patching code at runtime.
* **Impact**: Upgrading `mlx_lm` frequently breaks OMLX.
* **Handling**: Propose upstream PRs to MLX. Document internal patch limits.

### 2. Scheduler MLX Coupling
* **Classification**: Medium
* **Why**: The Scheduler is tightly coupled to MLX's `BatchGenerator`.
* **Impact**: Makes it harder to implement non-text/non-standard batching.
* **Handling**: Introduce an interface above `BatchGenerator`.

### 3. IOKit Memory Races
* **Classification**: High
* **Why**: Described in `omlx/scheduler.py` (`_DEFERRED_CLEAR_DELAY`). Kernel panics occur if `mx.clear_cache()` is called too aggressively.
* **Impact**: Stability vs TTFT (Time To First Token) tradeoff.
* **Handling**: Wait for better memory synchronization primitives from Apple/MLX.
