# PLUGIN-003: Security, Semantic Versioning, and Permissions

## Semantic Versioning Guide
oMLX uses `packaging.version` and `packaging.specifiers` to handle PEP-440 compliant version resolution. We also support npm-like specifiers (`^` and `~`) which are converted to PEP-440 internally.
Plugins should use constraints to express valid dependencies and required environments.

## Plugin Security Guide
oMLX enforces isolation and security boundaries strictly at boot-time. Plugins are verified based on their dependencies, explicit permissions, trust levels, and configuration policies.

## Permissions Guide
Plugins must explicitly declare needed permissions using the `PluginPermission` enum. Examples:
- `COMPILER_ACCESS`
- `PLANNER_ACCESS`
- `FILESYSTEM_READ`
