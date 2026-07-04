# Backend Capability Documentation

Capabilities define the feature support for a specific backend adapter.

- `AUTOREGRESSIVE`: Supports autoregressive generation.
- `DIFFUSION`: Supports diffusion model inference.
- `MULTIMODAL`: Supports multimodal (image/audio) execution.
- `EXPERT_ROUTING`: Supports Mixture-of-Experts routing strategies.
- `SPECULATIVE_DECODING`: Supports speculative/draft-based decoding.
- `GRAPH_EXECUTION`: Supports fully compiled graph execution.
- `ASYNC_EXECUTION`: Supports asynchronous non-blocking stream execution.
- `PAGED_KV_CACHE`: Supports paged Key-Value caching.
- `SSD_CACHE`: Supports NVMe/SSD offloading for caches.
- `PREFIX_CACHE`: Supports prompt prefix caching.
- `VERIFICATION`: Supports result/token verification steps.
- `DYNAMIC_BATCHING`: Supports runtime batching adjustments.
- `CONTINUOUS_BATCHING`: Supports continuous batch execution.
- `DISTRIBUTED_EXECUTION`: Supports multi-node execution.
- `RUNTIME_COMPILATION`: Supports JIT compilation.
