# Brand Migration Report

This report documents the migration from `oMLX` to `One` across the entire codebase, user-facing documentation, and interfaces.

## 1. Summary of Changes
The application has been completely rebranded to **One**. All user-facing occurrences of `oMLX`, `OMLX`, and associated names have been replaced with `One`.

## 2. Updated Components

### CLI & Backend Commands
- **Primary executable entrypoints**: Added support for both `one` and `omlx` scripts in `pyproject.toml`. The `one` command is now the primary user guidance instruction.
- **Help screens**: Rebranded `omlx` help and command-line usage examples to `one` inside [cli.py](file:///Users/yugeshk/dev/repo/omlx/omlx/cli.py).
- **Diagnostics**: Rebranded `omlx diagnose` subcommands to `one diagnose`.

### Server & APIs
- **Exception Messages**: Updated user-facing HTTP exceptions, including memory guard prefill errors in [server.py](file:///Users/yugeshk/dev/repo/omlx/omlx/server.py), to reference `One`.
- **FastAPI Metadata**: Rebranded the API title to `One API` in FastAPI initialization.
- **Session Cookie**: Rebranded the session authentication cookie to `one_admin_session`.

### Translations (i18n)
- Updated all 9 translation JSON files under [omlx/admin/i18n/](file:///Users/yugeshk/dev/repo/omlx/omlx/admin/i18n/) via a automated script to replace user-facing strings of `oMLX`/`OMLX`/`omlx` to `One`/`one`.

### Static Assets & UI Links
- **Favicon**: Replaced legacy `favicon.svg` with a modern premium cosmic digit "1" SVG brand icon.
- **Navbar logo**: Connected a custom brand asset (`logo.jpg`) at `/admin/static/img/logo.jpg`.
- **Documentation & Repository**: Rebranded all repository links (e.g. `github.com/jundot/omlx` -> `github.com/jundot/one`) and help guides.

## 3. Backward Compatibility
- Graceful fallback for `localStorage` items (`omlx-` prefix migration to `one-` prefix).
- Homebrew service control retains `omlx` target name in command integration to prevent service startup failures under the OS system managers.
