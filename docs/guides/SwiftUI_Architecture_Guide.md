# SwiftUI Architecture Guide

## MVVM Pattern
Each Screen (e.g., `ServerScreen`, `ModelsScreen`) owns a `ViewModel` for fetching and transforming data. The Views observe the ViewModel state.
For example, `ModelSettingsScreenVM` handles mapping API responses to local `@Published` values.

## Navigation
Navigation is accomplished using `NavigationSplitView`. `AppSection` enum types act as deep-link routing identifiers. `AppServices` publishes `requestedServerAnchor` to coordinate programmatic deep links across views.
