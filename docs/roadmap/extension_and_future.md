# Extension, Migration, and Future Quantization Guide

## Extension Guide

The framework is highly modular and extensible. Adding a new quantization format requires no modifications to the execution Engine, Backend Adapters, or Runtime orchestrators.

### Steps to Add a New Format
1. **Types**: Add the new format identifier to `QuantizationFamily` in `types.py`.
2. **Classifier**: Update `QuantizationClassifier` in `classifier.py` to pattern-match the specific metadata signature of the new format.
3. **Extractor**: Add specialized mapping rules in `QuantizationCapabilityExtractor` (`extractor.py`) to convert custom precision representations into the standardized `weight_precision`, `storage_precision`, and `required_kernels`.

## Migration Report (QUANT-001 -> QUANT-002)

### Changes Introduced
- **Immutability Hardening**: `QuantizationDescriptor` has strictly transitioned to dataclass immutability enforcing tuples and `MappingProxyType` instances.
- **Enhanced Types**: GGUF Q-series (Q2-Q8), EXL2, and oQ natively supported.
- **Structural Validation**: Implemented a stateless validation interface (`QuantizationValidator`) integrated directly into discovery pipelines.
- **Descriptor Amplification**: Added fields for packing properties, kernel bindings, and compression matrices.

### Deprecations
- Legacy file-sniffing functions relying on explicit string-matching of model weight filenames are deprecated. Quantization is exclusively metadata-driven.

## Future Quantization Guide

The architecture has been preemptively stabilized to support upcoming milestones:

- **QUANT-003**: Dynamic, runtime-injected quantization graphs. The `packing_information` and `dynamic_quantization` boolean flags pave the way for real-time activation quantizations.
- **SPEC-001**: Speculative execution targets. The `supports_speculative_decoding` flag is exposed for future tree-search validation models.
- **MOE-001**: Mixed-precision and sparse expert execution routes rely on the `mixed_precision` flag introduced in this iteration.
- **DIFF-001**: Non-autoregressive model integration benefits from decoupled quantization registries that don't hardcode language model dependencies.
