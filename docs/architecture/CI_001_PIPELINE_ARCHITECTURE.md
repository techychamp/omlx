# Pipeline Architecture

This document describes the modular CI/CD pipeline architecture for the oMLX platform.

## Architecture Diagram

```mermaid
graph TD
    PR[Pull Request / Push] --> CI[ci.yml - Orchestrator Dispatcher]
    
    CI --> ARCH[architecture.yml - Phase 2 Architecture & Lint]
    CI --> PTEST[python-tests.yml - Phase 3 pytest with Coverage]
    CI --> STEST[swift-tests.yml - Phase 4 swift test]
    CI --> PKG[packaging.yml - Phase 5 python/Swift Build]
    
    PKG --> SMOKE[runtime-smoke.yml - Phase 6 & 7 Runtime Smoke & Release tests]
    PKG --> PERF[performance.yml - Phase 8 Performance Regression]
    
    CI --> SEC[security.yml - Phase 9 Security Scan]
    CI --> DOCS[docs.yml - Phase 10 Docs Audit]
    
    SMOKE & PERF & SEC & DOCS --> REL[release.yml - Phase 11 Release Automation]
```

## Layer Layout & Reusability
The orchestrator `ci.yml` contains zero build logic and serves strictly as a dispatcher. Individual validation gates are split into dedicated, reusable workflows located under `.github/workflows/`. Common initialization steps (Python, Swift/Xcode, Dependency Caching) are extracted into composite GitHub Actions in `.github/actions/`.

## Caching Strategy
Caching is configured with lockfile hashes to guarantee consistency and avoid stale cache issues:
- **uv/pip dependencies**: Keyed by `hashFiles('pyproject.toml', 'uv.lock')`.
- **SwiftPM dependencies**: Keyed by `hashFiles('apps/omlx-mac/Package.resolved')`.
- **venvstacks layers**: Keyed by `hashFiles('pyproject.toml', 'uv.lock', 'packaging/venvstacks.toml')`.
- **Xcode DerivedData**: Keyed by build SHA.
