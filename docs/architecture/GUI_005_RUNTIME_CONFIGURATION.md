# GUI-005 Runtime Configuration

## Overview

Runtime Configuration refers to the sub-views deployed within `RuntimeAdministrationView`, specifically `RuntimeConfigurationCard` and `SessionManagementView`.

## RuntimeConfigurationCard

This component displays:
- **Host / Bind Address**
- **Port**
- **API Version**
- **Backend (e.g. MLX)**

It operates entirely off of the `ServerInfo` DTO provided by `PlatformViewModel`.

## SessionManagementView

This component enumerates active sessions running on the server:
- **Total Session Count**
- **Current active sessions with Session ID and Creation Date**

### Constraints & Placeholders
Because the current `v1` API does not expose endpoints to mutate sessions, the UI enforces a read-only policy. A disclaimer text states: *"Feature unavailable in current Runtime API (Rename, Delete, Merge, Export, Archive)"* to clearly indicate that editing features are not supported by the backend yet, satisfying API freeze requirements.
