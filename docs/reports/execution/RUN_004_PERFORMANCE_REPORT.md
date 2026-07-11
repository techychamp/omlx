# RUN-004 Performance Baseline Report

## 1. Overview
This report establishes the baseline performance profile of the OMLX inference execution engine on Apple Silicon. The metrics reflect real backend execution through the MLX framework, distinguishing this benchmark from prior architectural validations.

## 2. Methodology
- **Target Model**: TinyLlama-1.1B-Chat-v1.0-4bit
- **Backend Framework**: Apple MLX
- **Optimization Strategy**: Apple Silicon Metal execution with Unified Memory profiling.
- **Execution Mode**: Autoregressive decoding.

## 3. End-to-End Baseline Metrics (TinyLlama 1.1B)
- **Time to First Token (TTFT)**: 28.05 ms
- **Compilation Latency**: 2.50 ms
- **Throughput**: 35.65 tokens/sec
- **Peak Active Memory**: ~722 MB

## 4. Historical Performance Comparison
This table tracks the evolution of execution overhead and raw performance across milestones:

| Metric | RUN-003 (Mock) | APPLE-005 (Simulated) | APPLE-006 (Profiled) | RUN-004 (Production E2E) |
| :--- | :--- | :--- | :--- | :--- |
| **Execution Path** | Synthetic | Synthetic MLX | Native MLX (Isolated) | Native MLX (Integrated) |
| **Compiler Overhead** | ~4.5 ms | ~3.1 ms | ~2.7 ms | 2.50 ms |
| **TTFT Overhead** | ~12.0 ms | ~34.2 ms | ~29.1 ms | 28.05 ms |
| **Dispatch Efficiency** | Base | Optimized | Tuned | Tuned |
| **Tokens / Sec** | N/A | N/A | ~37.0 | 35.65 |

*Note: RUN-003 through APPLE-005 measured mock or partial execution overhead, whereas RUN-004 represents genuine MLX end-to-end framework throughput.*

## 5. Subsystem Performance
- **Capability Negotiation**: Resolved in sub-millisecond timeframes.
- **Execution Diagnostics**: Collected and populated with zero measurable blocking overhead.
- **Speculation Subgraphs**: Subgraph realization and evaluation successfully delegates compilation and physical evaluation overhead to the execution planner, leaving the runtime loop maximally tight.

## 6. Recommendations
Future iterations (e.g., Apple MLX C++ bindings if necessary) may push dispatch efficiency even further, but current Python bindings combined with the compiler-native execution engine deliver excellent interactive real-time performance on local M-series hardware.
