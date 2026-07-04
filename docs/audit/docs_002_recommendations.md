# Recommendations for DOCS-002

## 1. Archival of Legacy Documentation
Now that the core architectural specifications, runtime guides, compiler behavior, and migration roadmaps have been successfully consolidated into the unified `docs/` Developer Manual, the repository contains significant redundant documentation.

**Recommendation:**
DOCS-002 should actively focus on deleting and archiving the loose `RAES-*` (Architecture) and `IMP-*` (Implementation) markdown files located in the root directory and legacy subdirectories. These files represent historical planning and proposal phases that are now fully encoded in the active Developer Manual and the codebase.

### Files to target for cleanup:
*   Root `RAES-*.md` files (e.g., `RAES-010-Plugin-Architecture.md`, `RAES-011.md`, `RAES-012-Implementation-Report.md`).
*   Root `IMP-*.md` files (e.g., `IMP-005-Capability-Resolver-Report.md`).
*   Loose reports like `registry_architecture_report.md`, `implementation_report.md`, and `capabilities_walkthrough.md`.
*   The `docs/architecture/` legacy files (`RAES-014-Runtime-Bootstrap.md`, `RAES-015_architectural_constitution.md`, `RAES-017_master_implementation_roadmap.md`, `01-system-overview.md`, etc.) that have been superseded by `docs/architecture/reference.md`.

## 2. Integration with Build/Site Generators
**Recommendation:**
DOCS-002 should implement a documentation site generator (e.g., MkDocs or Sphinx) configured to consume the new `docs/` hierarchy, ensuring proper cross-linking, searchability, and Mermaid rendering in a hosted format.

## 3. Maintenance of the Glossary
**Recommendation:**
The newly established `docs/glossary/glossary.md` should be strictly maintained as part of the PR review process. Any new abstract term introduced via an ADR must be added to the Glossary.
