# Lifetime Realization Guide

Tensor lifetimes are realized as `RELEASE` nodes in the IR, based on tensor `last_use_step` values dictated by the MemoryPlan.
