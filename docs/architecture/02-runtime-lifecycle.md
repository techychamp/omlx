# Runtime Lifecycle

## Application Startup & CLI Lifecycle
1. `omlx/cli.py` handles the initial command parsing (`serve`, `start`, `stop`, `restart`, `launch`).
2. Arguments are processed into specific server configurations or client commands.
3. If `serve` is called, `serve_command()` initializes server-level variables.

## Configuration Lifecycle
1. Defaults are populated via `omlx/config.py` and CLI arguments.
2. `EngineConfig` and `SchedulerConfig` instances are derived from global settings and CLI inputs.

## Server Lifecycle
1. `ServerState` (`omlx/server.py`) is initialized, setting up the global environment.
2. The HTTP API via FastAPI is mounted.
3. `EnginePool` is instantiated at server startup and initialized based on the `model-dir` config.

## Engine Lifecycle
1. `EnginePool` dynamically allocates or re-uses `EngineCore` instances via `_LLMEngineLease` context managers.
2. `EngineCore` wraps mlx-lm models and delegates generation logic.

## Scheduler Lifecycle
1. The `Scheduler` (`omlx/scheduler.py`) is created during `EngineCore` initialization.
2. Requests are added to the waiting queue (`add_request`).
3. Continuous batching happens during generation loops (`step`), transitioning states from waiting -> running -> finished.

## Inference & Streaming Lifecycle
1. Handled by `ExecutionGraph` and specific generation strategies (Autoregressive, etc.).
2. The scheduler handles `step()` calls. Output collectors process `SchedulerOutput`.
3. Server routes (e.g. SSE in `api/`) stream these tokens back to clients using keepalive mechanics.

## Model Lifecycle
1. Models are discovered via `omlx/model_discovery.py`.
2. Loaded into memory as needed or eagerly via `EnginePool`.
3. Cached using hybrid caching/Paged SSD if enabled.

## Plugin Lifecycle
1. Discovered at initialization via `plugin_discovery.py` using `entry_points`.
2. Capabilities registered in `CapabilityRegistry`.

## Shutdown Lifecycle
1. Server receives a termination signal.
2. `EnginePool` clears active engines.
3. `mx.clear_cache()` is called.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant CLI
    participant Server
    participant EnginePool
    participant EngineCore
    participant Scheduler
    participant MLX

    CLI->>Server: serve_command()
    Server->>EnginePool: initialize()
    Server->>CLI: Start HTTP Server
    Note over Server: Incoming Request
    Server->>EnginePool: acquire engine lease
    EnginePool->>EngineCore: initialize/reuse
    Server->>EngineCore: generate()
    EngineCore->>Scheduler: add_request()
    loop Continuous Batching
        EngineCore->>Scheduler: step()
        Scheduler->>MLX: evaluate forward pass
        MLX-->>Scheduler: logits/tokens
        Scheduler-->>EngineCore: SchedulerOutput
        EngineCore-->>Server: yield token (stream)
    end
    Server->>EnginePool: release lease
```

## Engine Lifecycle Sequence Diagram

```mermaid
sequenceDiagram
    participant EnginePool
    participant EngineCore
    participant MLX_LM

    EnginePool->>EngineCore: Request engine for Model X
    alt Model X active
        EngineCore-->>EnginePool: Return lease
    else Memory available
        EnginePool->>EngineCore: initialize(model_path)
        EngineCore->>MLX_LM: load()
        EngineCore-->>EnginePool: Return lease
    else Memory tight
        EnginePool->>EngineCore: evict LRU engine
        EnginePool->>EngineCore: initialize(model_path)
        EngineCore-->>EnginePool: Return lease
    end
```

## Scheduler Lifecycle Sequence Diagram

```mermaid
sequenceDiagram
    participant Server
    participant Scheduler
    participant MLX

    Server->>Scheduler: add_request(prompt)
    Scheduler->>Scheduler: add to waiting queue
    loop step() called by EngineCore
        Scheduler->>Scheduler: move waiting to running
        Scheduler->>Scheduler: apply memory bounds
        Scheduler->>MLX: step(running requests)
        MLX-->>Scheduler: outputs
        Scheduler->>Scheduler: remove finished requests
        Scheduler-->>Server: yield outputs
    end
```
