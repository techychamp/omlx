# Security Pipeline

This document defines the static security validation steps executed on the oMLX repository.

## 1. Dependency Audit (`pip-audit`)
- **Action**: Runs `pip-audit --local`.
- **Purpose**: Audits python dependencies (direct and transitive) against the PyPA database of known vulnerabilities.
- **Fail conditions**: Any dependency matching a known vulnerability with active CVEs.

## 2. Secret Scan
- **Action**: Audits git commits and the working tree for common high-entropy credentials, private keys, and API tokens.
- **Fail conditions**: Detection of strings matching `BEGIN PRIVATE KEY` or other critical raw credential markers.

## 3. Code Security Scan (`bandit`)
- **Action**: Runs `bandit -r omlx -lll -ii`.
- **Purpose**: Scans the Python source tree for common security issues (e.g. usage of `eval`, insecure random number generators, or subprocess shells).
- **Fail conditions**: High-severity security issues.

## 4. License Audit
- **Action**: Scans all Python source files for standard SPDX licensing identifiers and checks for the existence of the `LICENSE` file.
- **Fail conditions**:
  - Missing repository `LICENSE` file.
  - Less than 80% coverage of Python files containing standard license tags (`SPDX-License-Identifier` or `Apache`).
