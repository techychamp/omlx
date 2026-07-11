# GUI-008 Consistency Report

## Component Reusability
To eliminate duplicated code and standardize the visual footprint, the following unified shared components are mandated:
- `LoadingView`
- `EmptyStateView`
- `ErrorStateView`
- `PlaceholderCard`
- `MetricCard`
- `SectionHeader`

## Layout and Styling Constraints
- Padding and Spacing are strictly preserved according to SwiftUI defaults combined with `theme.*` overrides.
- Background canvases consistently utilize `theme.windowBg` or `theme.cardBg` without raw approximations.

By refactoring all workspaces to conform to these shared components, we guarantee that error boundaries, no-data boundaries, and data representations are uniformly rendered across the product suite.
