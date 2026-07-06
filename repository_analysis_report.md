# Repository Analysis Report
Current repository inspection in `ModelDiscoveryFramework` is limited:
- Only reads `config.json`, `generation_config.json`, and `tokenizer_config.json`.
- Misses `tokenizer.json`, `special_tokens_map.json`, `README.md`, model index files, GGUF/MLX/safetensors metadata, license info, and repository tags.
- Does not extract context length accurately across all variants.
- Does not extract expert size and count correctly for MoE models, parameter count relies on metadata without fallback.
