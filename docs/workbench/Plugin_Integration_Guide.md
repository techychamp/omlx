# Plugin Integration Guide

## Workbench Plugins
Plugins can integrate into the Developer Workbench by injecting new modules into the `NavigationManager`.

## Flow
1. A plugin is loaded via `PluginManager`.
2. The plugin retrieves the active `DeveloperWorkbench` instance.
3. The plugin calls `workbench.navigation.register_module(CustomPluginModule())`.
4. The Workbench UI dynamically renders the new module.

This ensures zero changes are required to the Workbench architecture when new planning domains or features are introduced.
