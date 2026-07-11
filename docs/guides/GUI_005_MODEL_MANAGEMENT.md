# GUI-005 Model Management Workspace

## Overview

The Model Management workspace (`ModelManagementView`) provides a read-only interface for discovering, searching, and inspecting models that are loaded or installed on the system.

## Architecture & Data Flow

The view operates strictly according to the architecture laid out in `GUI_002_API_FREEZE.md`:

```text
ModelManagementView
    ↓
ModelManagementViewModel (State & Local Filtering)
    ↓
ModelManagementServiceProtocol
    ↓
OMLXClient
    ↓
Runtime (v1/models)
```

## Features

1. **Robust Local Filtering**: Users can filter models using a search bar. The filtering is strictly local, case-insensitive, and diacritic-insensitive.
2. **Stable Sorting**: Models can be sorted by name in ascending or descending order.
3. **Model Metadata Display**: We surface metadata that is strictly present in the DTO (e.g. `id`, `ready`, and `apiVersion`).
4. **Graceful Degradation**: For model properties and actions that are not currently exposed in the v1 API (e.g. Quantization, Parameters, Context Length, Installation, Editing), the view explicitly displays the placeholder: *"Unavailable via current Runtime API"*.
5. **Accessibility**: The view implements `accessibilityAddTraits`, `accessibilityLabel`, and `accessibilityElement(children: .combine)` for semantic navigation.

## Limitations

As per the API Freeze, this milestone does **not** implement downloading, installing, deleting, or configuring models. Those operations belong to future milestones that expand the backend API capabilities.
