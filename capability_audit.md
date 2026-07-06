# Capability Audit
Currently, `CapabilityExtractor` extracts only:
- kv_cache_support
- speculative_support
- streaming_support
- expert_support
- vision_support
- audio_support
- tool_support
- embedding_support
- reranking_support
- quantization_support
- attention_type
- backend_requirements

It misses out on granular capabilities like:
text generation, chat, instruction following, reasoning, code generation, classification, summarization, translation, function calling, JSON generation, continuous batching compatibility, Apple Silicon suitability.
Capabilities are hardcoded heuristics rather than inferred properly from robust metadata signatures.
