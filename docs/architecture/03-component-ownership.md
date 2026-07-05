# Component Ownership Map

This document outlines the ownership semantics for major runtime subsystems.

| Subsystem | Who creates it? | Who owns it? | Who mutates it? | Who destroys it? | Who depends on it? |
|---|---|---|---|---|---|
| **Scheduler** (`omlx/scheduler.py`) | `EngineCore` | `EngineCore` | `EngineCore` (via `add_request`, `step`, `abort_request`) | `EngineCore` (garbage collection when engine dies) | `EngineCore`, Server API (indirectly) |
| **EnginePool** (`omlx/engine_pool.py`) | `ServerState` (`omlx/server.py`) | `ServerState` | `ServerState` (via requests to acquire leases) | Application Exit | `Server` (for request handling) |
| **EngineCore** (`omlx/engine_core.py`) | `EnginePool` | `EnginePool` (managed via lease context) | `Server` (adds requests) | `EnginePool` (when releasing / evicting) | `EnginePool`, Server routes |
| **ExecutionBackend** (`omlx/inference/backends/`) | `EngineCore` / Strategy | `EngineCore` | Inference strategies | `EngineCore` | Execution Pipelines |
| **ExecutionPipeline** | Strategy logic | Strategy | Strategy | Strategy / GC | `EngineCore` |
| **ExecutionGraph** (`omlx/inference/execution_graph.py`) | Generation Strategies (e.g. `build_autoregressive_graph`) | The specific inference call | Read-only structural graph | GC | Generation Logic |
| **ExecutionContext** (`omlx/runtime/context.py`) | Request handler / Engine | Lifecycle of request | `EngineCore`, `Scheduler` | Request Completion | Scheduler, Metrics, Caching |
| **Settings** (`omlx/settings.py`) | CLI/Global Setup | Application | Admin APIs (if mutable) | N/A (Global) | Almost all subsystems |
| **Registry** (`omlx/registry/`) | Application Startup | Global scope | `discover_plugins()` | N/A | Capabilities |
| **Capabilities** (`omlx/runtime/capabilities.py`) | Registry/Engine | Engine | Static per-engine | Engine shutdown | API validation |
| **Streaming** (`omlx/inference/streaming.py`) | Server endpoints | HTTP Response | Async Generators (`EngineCore` output) | Connection Close | API Clients |
| **Caching** (`omlx/cache/`) | `ServerState` / `EngineCore` | Server / EngineCore | `Scheduler`, `EngineCore` (adding/evicting blocks) | Application Exit | Scheduler, MLX backend |
| **Metrics** (`omlx/runtime/metrics.py`) | Subsystems (Scheduler, Engine) | Global/Singleton | All subsystems (stats emission) | N/A | Prometheus/Observability |
| **Plugins** (`omlx/registry/plugin_discovery.py`) | Startup Discovery | Registry | N/A (loaded once) | N/A | Inference capabilities |
| **Model Discovery** (`omlx/model_discovery.py`) | Server/EnginePool | `EnginePool` | `EnginePool` (rescans) | N/A | `EnginePool`, API Routes |
| **Model Registry** (`omlx/model_registry.py`) | System | System | Admin Config | N/A | `EnginePool` |
