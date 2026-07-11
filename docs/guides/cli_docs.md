# CLI Documentation

The Validation CLI is accessed via `python -m omlx.tooling.cli.main` (or exposed as a bin script depending on setup).

## Commands
- `inspect-plan <file>`: Reads a JSON plan dump and pretty-prints it.
- `inspect-ir <file>`: Reads a JSON IR dump and prints structural info.
- `export-graph <file> --format <fmt>`: Converts an IR graph to the specified format (dot, mermaid, yaml, etc.).
- `compare-plans <file1> <file2>`: Executes the `CompilerDiffer` against two plans and highlights added/removed elements.

All CLI commands are strictly read-only and operate on exported artifacts, ensuring runtime safety.
