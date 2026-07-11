# Execution Flows

## Text Generation (Autoregressive)
* **Entry point**: `omlx/api/shared_models.py` (via `omlx/server.py` routing)
* **Execution path**: HTTP -> EnginePool -> EngineCore -> Autoregressive Strategy -> Scheduler -> MLX BatchGenerator
* **Major components**: `EngineCore`, `AutoregressiveStrategy`, `Scheduler`, `paged_ssd_cache`
* **Exit point**: `omlx/api/adapters/` (formatting outputs back to SSE/JSON)

## Embeddings
* **Entry point**: `omlx/api/embedding_routes.py`
* **Execution path**: HTTP -> EnginePool (requests EmbeddingEngine) -> EngineCore -> `EmbeddingStrategy` -> Scheduler -> MLX
* **Major components**: `EngineType.EMBEDDING`, `omlx/engine/embedding.py`
* **Exit point**: JSON response of embeddings.

## Reranking
* **Entry point**: `omlx/api/rerank_routes.py`
* **Execution path**: HTTP -> EnginePool -> `RerankerEngine` -> MLX cross-encoder forward pass
* **Major components**: `omlx/engine/reranker.py`, `omlx/models/reranker.py`
* **Exit point**: JSON array of documents sorted by score.

## Vision (VLM)
* **Entry point**: Chat completions route with multimodal input.
* **Execution path**: Image parsing -> Feature extraction (via cache) -> Token injection -> Autoregressive generation
* **Major components**: `omlx/engine/vlm.py`, `omlx/models/vlm.py`, `vision_feature_cache.py`
* **Exit point**: Standard SSE/JSON response.

## MCP (Model Context Protocol)
* **Entry point**: `omlx/mcp/client.py` or MCP API routes.
* **Execution path**: External MCP server -> Tool registration -> Chat generation -> Tool calling loop
* **Major components**: `omlx/mcp/manager.py`, `omlx/mcp/executor.py`, `omlx/mcp/tools.py`
* **Exit point**: Tool output injected back into context or sent to client.

## Streaming
* **Entry point**: Client sets `stream=True`.
* **Execution path**: `EngineCore.generate()` yields an AsyncGenerator -> `sse_formatter.py` wraps in SSE protocol.
* **Major components**: `omlx/inference/streaming.py`, `omlx/api/adapters/sse_formatter.py`
* **Exit point**: HTTP chunked transfer encoding stream.

## Experimental Diffusion
* **Entry point**: Image generation endpoint.
* **Execution path**: HTTP -> EnginePool -> Diffusion Engine -> Denoising Loop
* **Major components**: `omlx/inference/backends/experimental_diffusion_backend.py`
* **Exit point**: Base64 or bytes image response.
