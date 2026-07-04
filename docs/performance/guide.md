# Performance Guide

## 1. Overview
oMLX is optimized for high-performance inference on Apple Silicon. Any architectural shifts, compiler additions, or backend modifications must strictly adhere to established performance budgets.

## 2. Strict Performance Budgets
To prevent regressions during the implementation of the new Execution Planner and Plugin Architecture, oMLX enforces the following strict performance budgets. Changes exceeding these budgets will fail CI fitness gates:

*   **Time To First Token (TTFT):** `< 2%` regression.
*   **Tokens Per Second (TPS):** `< 3%` regression.
*   **Peak RAM Usage:** `< 5%` regression.
*   **Peak VRAM Usage:** `< 3%` regression.
*   **Plugin Framework Overhead:** `< 1%` overhead on request lifecycle.
*   **Planner Compilation Overhead:** `< 0.5%` overhead on total execution time.

## 3. Compiler & Optimization Pipeline
To maintain the `< 0.5%` planner overhead, the `ExecutionPlanner` relies on:
*   **Compiler Cache:** Frequently used Capability Descriptors and their resulting Physical IR plans should be cached.
*   **Incremental Compilation:** Avoiding full graph re-evaluations for minor parameter tweaks.
*   **Graph Reuse:** The Execution Engine leverages the backend Operation Graph across sequential batches when the topology hasn't changed.

The `PassManager` utilizes a Cost Model to evaluate latency, memory, and cache pressure before applying rewrite passes, ensuring optimizations actually yield performance gains on the target hardware.
