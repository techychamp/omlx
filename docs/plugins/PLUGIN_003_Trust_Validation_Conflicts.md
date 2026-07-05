# PLUGIN-003: Trust, Validation, and Conflict Resolution

## Trust Model Guide
Trust in oMLX ranges from `CORE` down to `UNTRUSTED`. A plugin with high trust (`CORE`, `VERIFIED`) cannot depend on an untrusted plugin.

## Validation Guide
`PluginValidationFramework` runs strictly at startup, evaluating descriptor consistency, trust relationships, isolation flags, and capabilities.

## Conflict Resolution Guide
Conflicts (duplicate extensions, mismatched versions, and trust boundary violations) are detected deterministicly without modifying runtime execution.
