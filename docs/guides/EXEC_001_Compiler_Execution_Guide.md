# Compiler Execution Guide

This milestone shifts `Runtime` to compiler-driven execution. `Runtime` checks for the feature flag `COMPILER_RUNTIME_ENABLED` and creates the `ExecutionContext` with pipeline artifacts, shifting legacy logic into a purely deterministic, compiler-managed sequence.
