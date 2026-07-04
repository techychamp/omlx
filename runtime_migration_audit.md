# Runtime Migration Audit

## Entry Points
- `/v1/completions`: `create_completion`
- `/v1/chat/completions`: `create_chat_completion`
- `/v1/embeddings`: `create_embeddings`
- `/v1/rerank`: `create_rerank`
- `/v1/messages`: `create_messages` (Anthropic compatibility)

## Runtime Initialization
- `omlx.server.init_server` initializes the `RuntimeBuilder` which constructs the `Runtime`.
- Subsystems initialized include: `EnginePool`, `CapabilityResolver`, `ExecutionPlanner`, `IRBuilder`, `LoweringEngine`, `AdapterRegistry`, and `BackendDescriptorRegistry`.
- Everything is managed under `_server_state.runtime` and `_server_state.engine_pool`.

## EnginePool Request Lifecycle
- `EnginePool.get_engine` handles LRU eviction, memory checking, and loads the model into a `BaseEngine` (e.g., `BatchedEngine`).
- `BatchedEngine` runs a continuous batching loop via a `Scheduler`.

## EngineCore Execution Flow
- `EngineCore` wraps `BatchedEngine`. Requests are submitted via `EngineCore.add_request`.
- The generation loop runs on an independent thread, executing `scheduler.step()`.

## ExecutionProfile Usage
- Used in legacy execution to define parameters, backend factory, and context constraints.
- Will eventually be superseded by `ExecutionPlan` derived from `CapabilityDescriptor`.

## Model Loading Flow
- `get_engine_for_model` -> `get_engine` (with lease) -> `pool.get_engine`.
- Model parameters and tokenizer are loaded via HF integrations, passed into the `BatchedEngine` constructor.

## Execution Backend Entry Points
- Models use custom execution routines embedded in `BatchedEngine` or backend-specific generators.

## Scheduler Entry Points
- The `Scheduler` (omlx.scheduler) performs batch generation scheduling. The compiler will not modify this in this phase.

## Current Inference Pipeline
- Request -> Tokenization -> EnginePool Lease -> EngineCore submit -> Scheduler -> Backend.
- We will integrate the compiler pipeline immediately after the `EnginePool` lease, without blocking the backend execution.
