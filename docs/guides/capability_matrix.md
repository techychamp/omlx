# Capability Matrix

This matrix describes the specific execution capabilities for each generation and decoding paradigm.

| ExecutionCapabilities | Autoregressive (Causal) | Diffusion (Nemotron/Gemma) | Triage (Self-Speculation) | Streaming MoE |
| :--- | :---: | :---: | :---: | :---: |
| **`supports_autoregressive`** | **True** | False | **True** | **True** |
| **`supports_diffusion`** | False | **True** | **True** | False |
| **`supports_triage`** | False | False | **True** | False |
| **`supports_verification`** | False | False | **True** | False |
| **`supports_streaming_moe`** | False | False | False | **True** |
| **`supports_speculative`** | False | False | **True** | False |
| **`supports_bidirectional`** | False | **True** | False | False |
| **`supports_chunk_generation`**| False | **True** | **True** | False |

---

### Description of Capabilities

*   **`supports_autoregressive`**: Causal left-to-right decoding, generating exactly one token per forward pass.
*   **`supports_diffusion`**: Parallel decoding of a block of tokens via iterative refinement (denoising).
*   **`supports_triage`**: Dynamic routing or switching between decoding modes (e.g., deciding whether to generate or verify) based on sequence context or confidence thresholds.
*   **`supports_verification`**: Scoring/validating a block of candidate draft tokens using a causal attention mask (typically in a single forward pass).
*   **`supports_streaming_moe`**: Fine-grained, step-by-step token generation where Mixture-of-Experts routing is monitored for streaming memory overhead and active expert footprint.
*   **`supports_speculative`**: Non-autoregressive drafting (using an auxiliary model, draft heads, or self-speculation) paired with validation.
*   **`supports_bidirectional`**: Non-causal attention within the generation block where tokens attend to both left and right neighbors in the same block.
*   **`supports_chunk_generation`**: Emitting blocks or chunks of multiple tokens at a time instead of single-token deltas.
