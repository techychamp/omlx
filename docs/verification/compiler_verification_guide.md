# Compiler Verification Guide

## Purpose
This guide outlines the methodology for verifying the compiler invariants, such as immutability, graph consistency, analysis correctness, operation ordering. Verification must not execute model inference.

## Verifiers
- `CompilerInvariantVerifier`: verifies invariants and graph states.
