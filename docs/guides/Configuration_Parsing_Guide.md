# Configuration Parsing Guide

## Mechanism
`MetadataNormalizer` ingests `config.json`, `generation_config.json`, and `tokenizer_config.json` to synthesize a standardized metadata dictionary. Missing values fall back to defaults or are inferred.
