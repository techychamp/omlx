# Validation Architecture Report

## Previous State
Validation resided in `validate_capabilities()` inside `validation.py`, implementing a hardcoded sequence of `if-else` conditionals. Scaling this approach would result in massive, unmaintainable control flows and potential cross-rule contamination.

## Extensible Architecture
We refactored capability validation into a strict, Rule-based Engine.

- **`ValidationRule`**: A completely stateless ABC providing the standard contract `validate(caps: dict)`.
- **Concrete Rules**: Hardcoded logic was isolated into independent, focused rules:
  - `DiffusionStreamingRule`
  - `DiffusionAttentionRule`
  - `EmbeddingStreamingRule`
  - `AutoregressiveAttentionRule`
- **`ValidationRegistry`**: Owns a frozen list (`tuple`) of active validation rules, ensuring thread safety post-initialization.
- **`ValidationEngine`**: Iterates through the registered rules and invokes `validate` against the generated configurations.

## Compliance
- **Extensibility**: Future developers only need to define a new `ValidationRule` and inject it through `CapabilityResolver(validation_rules=[...])` without modifying existing logic.
- **Thread Safety**: All active concrete rules are strictly stateless. Rules operate only on the provided parameter `caps` dict. They do not mutate the dictionary or cache internal data across evaluations.
