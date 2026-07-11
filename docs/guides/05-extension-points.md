# Extension Point Audit

This document audits the extension mechanisms within OMLX.

## 1. Capability Negotiation
* **Location**: `omlx/registry/capability_registry.py`, `omlx/runtime/capabilities.py`.
* **Extensibility**: High. Registries allow dynamic declaration of supported features (e.g. vision, tool calling) per model.
* **Stability**: Stable.
* **Future Work**: Should be reused for registering Diffusion or Nemotron specific capabilities.

## 2. Execution Backend
* **Location**: `omlx/inference/backends/`.
* **Extensibility**: Medium. Requires implementing `ExecutionBackend` interface.
* **Stability**: Evolving. Currently has `autoregressive` and `experimental_diffusion`.
* **Future Work**: Suitable for extending custom execution runtimes.

## 3. Plugin Discovery
* **Location**: `omlx/registry/plugin_discovery.py`.
* **Extensibility**: High. Uses Python `entry_points` (`omlx.strategies`).
* **Stability**: Stable.
* **Future Work**: Third parties can inject new architectures without core changes.

## 4. Model Discovery
* **Location**: `omlx/model_discovery.py`.
* **Extensibility**: Medium. Hardcoded to specific directory scanning and HuggingFace Hub logic.
* **Stability**: Stable.

## 5. Model Profiles
* **Location**: `omlx/model_profiles.py`.
* **Extensibility**: High. JSON/dict based profile overrides.
* **Stability**: Stable.
* **Future Work**: Future execution profiles (e.g., Triage) should integrate here.

## 6. Streaming
* **Location**: `omlx/inference/streaming.py`, `omlx/api/adapters/sse_formatter.py`.
* **Extensibility**: Low. Tightly coupled to SSE standards.
* **Stability**: Stable.

## 7. Caching
* **Location**: `omlx/cache/` (e.g. `interface.py`, `factory.py`).
* **Extensibility**: High. Interface-driven (`CacheManager`). Supports Paged, Paged SSD, Hybrid.
* **Stability**: Stable.

## 8. Scheduler Hooks
* **Location**: `omlx/scheduler.py`, `omlx/registry/capability_registry.py` (`SchedulerHooks`).
* **Extensibility**: Medium.
* **Stability**: Stable.
* **Future Work**: Dynamic execution planning may require more invasive hooks here.

## 9. Configuration
* **Location**: `omlx/config.py`, `omlx/settings.py`.
* **Extensibility**: Medium. Environment variable and CLI driven.
* **Stability**: Stable.

## 10. Model Loading
* **Location**: `omlx/utils/model_loading.py`.
* **Extensibility**: Low. Wraps `mlx_lm.load` directly.
* **Stability**: Stable, but reliant on upstream MLX-LM.
