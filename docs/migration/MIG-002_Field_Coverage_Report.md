# MIG-002: Field Coverage Report

This document categorizes every field in the legacy `ExecutionProfile` relative to the canonical `ExecutionPlan`.

## Coverage Summary
- **Total Fields**: 7
- **Coverage**: 100%

## Field Breakdown

### 1. `backend_name`
- **Classification**: Mapped (Canonical Source)
- **Source**: `ExecutionPlan.execution_backend`
- **Mapping Logic**: Direct forwarding. `ExecutionPlanner` strictly controls backend selection.

### 2. `attention_mode`
- **Classification**: Mapped (Hint)
- **Source**: `ExecutionPlan.execution_hints["attention_mode"]`
- **Mapping Logic**: Direct forwarding if present; otherwise, falls back to the dataclass default (`"causal"`).

### 3. `cache_mode`
- **Classification**: Mapped (Static Translation)
- **Source**: `ExecutionPlan.cache_strategy`
- **Mapping Logic**: Mapped from `CacheLayoutType` enum via a static dictionary (`CACHE_MODE_MAP`).

### 4. `sampler_mode`
- **Classification**: Mapped (Hint)
- **Source**: `ExecutionPlan.execution_hints["sampler_mode"]`
- **Mapping Logic**: Direct forwarding if present; otherwise, falls back to the dataclass default (`"standard"`).

### 5. `streaming_mode`
- **Classification**: Mapped (Canonical Source)
- **Source**: `ExecutionPlan.execution_mode`
- **Mapping Logic**: Direct forwarding.

### 6. `position_encoding`
- **Classification**: Mapped (Hint)
- **Source**: `ExecutionPlan.execution_hints["position_encoding"]`
- **Mapping Logic**: Direct forwarding if present; otherwise, falls back to the dataclass default (`"rope"`).

### 7. `version`
- **Classification**: Mapped (Hint)
- **Source**: `ExecutionPlan.execution_hints["version"]`
- **Mapping Logic**: Direct forwarding if present; otherwise, falls back to the dataclass default (`"v1"`).

## Conclusion
`ExecutionProfile` contains **zero** unmapped fields. There are **zero** missing fields that the legacy scheduler expects that the adapter cannot supply. There is **zero** planning logic within the adapter itself.
