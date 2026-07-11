# GUI-008 Appearance

## Theme Management
`AppearanceManager` dynamically controls the application theme, exposing `.system`, `.light`, and `.dark` overrides via `@AppStorage`.

## Token Enforcement
A global codebase audit was performed to replace hardcoded `Color.white`, `Color.black`, and `Color.gray` literals with robust standard tokens (`Color.primary`, `Color(theme.border)`).

This ensures consistent contrast and layout integrity across macOS appearance changes, reducing technical debt.
