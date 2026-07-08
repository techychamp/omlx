# GUI-008 Accessibility Audit

## Findings
The application was audited against macOS SwiftUI accessibility standards.

- **VoiceOver:** Labels (`.accessibilityLabel`) and traits are fully assigned to Shared Components (`LoadingView`, `EmptyStateView`, `ErrorStateView`, `PlaceholderCard`, `MetricCard`).
- **Keyboard Navigation:** Native `.plain` and `.borderedProminent` ButtonStyles correctly register focus rings.
- **Shortcuts:** Core pathways are accessible via Keyboard Shortcuts (e.g., ⌘K for Command Palette).
- **Dynamic Type:** All textual displays utilize scalable semantic fonts (e.g., `.headline`, `.body`, `.caption2`) instead of fixed point sizes.
- **Contrast & Motion:** High-contrast `OMLXTheme` tokens are strictly enforced. Avoidance of non-semantic structural animations aligns with Reduced Motion guidelines.
