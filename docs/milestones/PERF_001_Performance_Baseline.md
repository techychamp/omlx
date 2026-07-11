# Milestone Plan — PERF-001: Performance Regression Baseline

This milestone establishes a standard suite of benchmark records to track and identify any performance regressions across future releases.

---

## 1. Metrics & Recording Specifications

### Task 1.1: Startup Metrics
- **Objective**: Measure the time elapsed from executable launch to server active state.
- **Metric**: Milliseconds to reach health state.

### Task 1.2: Memory Usage
- **Objective**: Profile memory footpint at various load states.
- **Metrics**: 
  - RSS (Resident Set Size) at idle.
  - Peak Metal allocator memory during prefill and generation.
  - Eviction time under model switching.

### Task 1.3: Inference Latency
- **Objective**: Track generation speeds for standard model families.
- **Metrics**:
  - Time-to-First-Token (TTFT) in milliseconds.
  - Inter-token latency (tokens per second).

### Task 1.4: GUI Responsiveness
- **Objective**: Profile UI main thread blocking during active background processing.
- **Metric**: Frame drop rates or Main-thread hangs during model downloads/serving.

### Task 1.5: Compilation & Bundle Sizes
- **Objective**: Prevent bloat in compiled output and bundle assets.
- **Metrics**:
  - Total bundle size of staged `One.app` (in MB).
  - Wheel build and venvstacks packaging compilation time (in seconds).
