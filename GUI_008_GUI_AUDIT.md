# GUI-008 GUI Audit

## Issues Found & Resolved
- **Hardcoded Colors:** Legacy screens incorrectly used `Color.white`, `Color.black`, and `Color.gray`. These have been successfully migrated to `Color.primary` and `Color(theme.border)` / `Color(theme.cardBg)`.
- **Component Duplication:** Identified overlapping responsibilities in placeholders. Consolidated these to `PlaceholderCard` and `EmptyStateView` within `Theme/Components`.
- **Window Management Loss:** The UI previously lost context entirely upon window closes. This has been solved via `WindowStateManager` tracking user state locally.

## Remaining Technical Debt
- Some legacy screens (e.g., `DownloadsScreenVM`, `SecurityScreenVM`) still take `OMLXClient` directly into functions rather than relying completely on robust Service protocols. While acceptable given the API freeze, migrating these to modern Service protocols will be required during RUN-005/API v2 updates.
- Global Search currently returns results based on statically available local states due to the missing comprehensive search endpoints in the `v1` backend API. Further search expansion depends on robust query capabilities deployed in future iterations.
