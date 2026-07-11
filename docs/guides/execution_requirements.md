# Execution Requirements

This document specifies the lower-level execution requirements for each paradigm, mapping physical compute needs to the repository's interfaces.

---

## 1. Nemotron-Labs-Diffusion-3B (Diffusion Mode)

*   **Execution Topology**: Sequential block refinement stages (Init -> Iterate Refinement/Forward -> Finalize). The generation traverses the diffusion execution graph [build_diffusion_graph](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/execution_graph.py#L76-L83) sequentially.
*   **Attention**: Causal for the prefix (condition part); block-diagonal for the generation block (tokens within the block attend to each other).
*   **Masking**: Constructed in [NemotronModelAdapter.create_diffusion_mask](file:///Users/yugeshk/dev/repo/omlx/omlx/models/adapters/nemotron_adapter.py#L31-L85). It combines:
    1.  Causal masking for indices `< prefix_len`.
    2.  Offset block-causal masking for indices `>= prefix_len` attending to indices `< prefix_len`.
    3.  Block-diagonal masking for indices `>= prefix_len` attending to indices `>= prefix_len` within the same block.
*   **Cache**: Caching is required only for the prefix/condition. The active diffusion generation block does not utilize KV caching since tokens at these positions are updated/refined simultaneously in parallel rather than generated autoregressively.
*   **Scheduler Implications**:
    *   Continuous batching is bypassed or limited because a request completes block-by-block rather than token-by-token.
    *   Scheduler step loops must invoke `strategy.forward()` instead of direct calls to `BatchGenerator`.
    *   Requires scheduler event hooks like `AFTER_EMIT` [diffusion.py:L87](file:///Users/yugeshk/dev/repo/omlx/omlx/inference/strategies/diffusion.py#L87) to update metrics.
*   **Tokenizer**: Custom chat templates. Standard detokenization.
*   **Streaming Feasibility**: Fully feasible at the block level. The engine yields the text once the block denoising iterations finish (typically 3-8 iterations per block).

---

## 2. Diffusion Gemma

*   **Execution Topology**: Sequential block generation using `stream_diffusion_generate`.
*   **Attention**: Custom multi-stage block attention patterns native to Gemma 4 reasoning architecture.
*   **Masking**: Handled internally by the `mlx-vlm` library's generator.
*   **Cache**: The KV cache is managed internally by `mlx-vlm`'s generation stream. oMLX's external scheduler-level caching must be disabled or bypassed.
*   **Scheduler Implications**:
    *   Currently runs under a serialization lock (`self._diffusion_lock` in [vlm.py:L3710](file:///Users/yugeshk/dev/repo/omlx/omlx/engine/vlm.py#L3710)), which limits concurrency to 1 request.
    *   Future batched scheduler execution requires exposing `mlx-vlm`'s step functions directly to the execution backend.
*   **Tokenizer**: Gemma 4 chat template. Has special tool calling markers and reasoning markers (thought-channel `<|channel>thought\n`, `<channel|>`, and `<turn|>`).
*   **Streaming Feasibility**: Emits detokenized text segments when a block is completed (`result.diffusion_block_complete == True`). Uses a `gemma4` output parser session [vlm.py:L3584](file:///Users/yugeshk/dev/repo/omlx/omlx/engine/vlm.py#L3584) to filter protocol markers and format thought blocks as `<think>...</think>`.

---

## 3. Nemotron Labs 3B Triage Mode

*   **Execution Topology**: Hybrid/nested DAG (Prefill -> Draft via Diffusion -> Verify via Autoregressive -> Accept -> Emit).
*   **Attention**: Hybrid: toggles between block-diagonal (for fast parallel drafting) and causal (for verification).
*   **Masking**: Dynamic mask swapping. During the drafting phase, the model adapter applies the block-diagonal diffusion mask. During the verification phase, it applies standard causal masking.
*   **Cache**: The KV cache must support partial/speculative eviction (discarding keys for rejected draft tokens) and key alignment.
*   **Scheduler Implications**:
    *   Variable-length step processing. The scheduler must support speculative drafting and verification cycles.
    *   The number of tokens generated per step is dynamic (equal to the number of accepted draft tokens).
*   **Tokenizer**: Standard tokenizer, but requires alignment between draft token candidates and verification token ids.
*   **Streaming Feasibility**: Token-level streaming of *accepted* tokens only. Discards speculative draft tokens until they are formally verified.

---

## 4. Streaming MoE execution

*   **Execution Topology**: Sequential layer-by-layer forward pass with dynamic conditional expert routing.
*   **Attention**: Causal or sparse-attention (e.g. `SpecPrefill` or minimax sparse attention).
*   **Masking**: Standard causal.
*   **Cache**: Normal KV cache, but experts themselves might need dynamic memory allocation or offloading.
*   **Scheduler Implications**:
    *   High prefill memory requirements.
    *   Needs a scheduling policy that balances active memory ceilings (via `ProcessMemoryEnforcer` [engine_pool.py:L1199](file:///Users/yugeshk/dev/repo/omlx/omlx/engine_pool.py#L1199)) and token throughput.
*   **Tokenizer**: Standard.
*   **Streaming Feasibility**: Fully feasible token-by-token. Emits tokens as they are produced at each step.
