# RUN-004 Known Limitations

## 1. Overview
The OMLX platform has achieved a stable architectural foundation. However, due to upstream constraints within Apple MLX and current scope boundaries, several limitations exist. These are explicitly catalogued here to guide future feature planning and backend adaptations.

## 2. Upstream Dependencies
- **Nemotron Model Architecture**: Upstream `mlx-lm` currently does not offer native first-class support for Nvidia's Nemotron models. Consequently, execution fails safely during capability resolution with a `404` or similar artifact absence.
- **Mixtral/MoE Models**: The validation suite encountered an upstream `404` for Mixtral weights. Additionally, sophisticated speculative routing for Mixture of Experts (MoE) is theoretically supported by the OMLX graph API, but practically bounded by `mlx-lm` expert memory overhead limits on smaller M-series chips.
- **Diffusion Execution**: Apple's MLX does not support high-performance diffusion topologies (e.g., Stable Diffusion) natively through the LLM interfaces yet. While the OMLX runtime architecture anticipates a `DiffusionExecutionGraph`, actual generation attempts will hit `CapabilityResolver` limitations.

## 3. Platform Limitations
- **Memory Profiling Precision**: The `mx.metal.get_peak_memory()` function (and its non-metal aliases) tracks global allocation bounds, but granular sub-kernel temporary allocation tracking remains opaque. As such, OMLX Memory Contexts conservatively over-estimate peak memory padding to prevent out-of-memory errors on 16GB Apple Silicon machines.
- **Session Scale Ceilings**: While 100 concurrent sessions processed within ~50ms of dispatch latency, the physical execution limit of concurrent LLM batches is bounded purely by memory. Realistically, concurrent batch size is tightly constrained by available unified memory, not Python dispatch limits.

## 4. Planned Resolutions
- Wait for `mlx-lm` upstream to introduce Nemotron and extended MoE topologies.
- Continue tracking Apple's official `mlx-examples` for diffusion integrations to implement the `DiffusionExecutionStrategy`.
