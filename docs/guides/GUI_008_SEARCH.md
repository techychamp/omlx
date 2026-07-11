# GUI-008 Global Search

## Command Palette
Global Search is implemented as a Spotlight-style Command Palette invoked via `⌘K` across the entire application.

## Search Aggregation
`GlobalSearchViewModel` aggregates results by injecting `AppServices` and concurrently fetching:
- Navigation Targets
- Models (via `ModelManagementService`)
- Sessions (via `SessionService`)
- Diagnostics and Compiler metadata

## API Compliance
The search functionality is entirely local to the GUI layer, relying *only* on the DTOs exposed by the frozen API. It performs case-insensitive and diacritic-insensitive filtering on the UI thread without introducing new search-specific endpoints.
