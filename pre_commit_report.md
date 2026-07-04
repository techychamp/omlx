## Summary
Generated the Architectural Constitution Document (RAES-015) to define the constitutional rules governing how the architecture evolves while preserving stability, extensibility, backward compatibility, and maintainability.

## Architecture impact
This is a design-only checkpoint and documentation update. No runtime changes were introduced. All architectural decisions established in RAES-001 through RAES-014 are preserved. The document establishes immutable rules (invariants) and sets a hierarchy for architectural decisions.

## Files changed
- `docs/architecture/RAES-015_architectural_constitution.md` (Added)

## Verification evidence
- The markdown document was successfully created at the target path.
- The pytest test collection issue observed (`No module named 'omlx'`) is due to environment setup (missing `mlx` on non-Mac or improper path) and is expected given the platform requirements for `mlx`, but it does not affect this design documentation task. The repository rules from `AGENTS.md` and RAES directives were strictly followed.

## Risks
None. It's a documentation file.

## Remaining work
None for this specific task.

## Recommendation
Approve and commit the architectural constitution document.

## Confidence
High. The document covers all requested sections, includes all user suggestions (Architecture Decision Hierarchy, explicit Architectural Invariants, Architectural Fitness Functions, Architectural Exceptions process, Governance Roles, Architectural Maturity Levels, expanded Compatibility Matrix, and Constitution Compliance Checklist), and provides the 8 required Mermaid diagrams.
