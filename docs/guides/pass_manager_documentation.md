# Pass Manager Documentation

The `PassManager` handles the registration and ordering of compiler passes.

## Responsibilities
- **Registration**: Allows passes to be registered via `.register()`.
- **Validation**: Uses the validation module to check for missing dependencies, circular dependencies, and conflicting passes.
- **Ordering**: Resolves dependencies using a topological sort, ensuring that `required_passes` and `optional_passes` are executed before the dependent pass.
