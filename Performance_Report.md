# Performance Report

This report documents the build optimization and rendering performance of the One Admin Dashboard.

## 1. CSS Build Footprint
The Tailwind CSS compilation is orchestrated by [build_css.py](file:///Users/yugeshk/dev/repo/omlx/omlx/admin/build_css.py).
- **Compilation Speed**: Tailwind CSS compiles in approximately **74ms**.
- **Bundle Optimization**: The production stylesheet `tailwind.css` is minified to **5,697 bytes**.
- **Unused Selector Purging**: The compiler inspects templates and javascript assets to purge unused Tailwind classes, ensuring a lightweight CSS asset.

## 2. Rendering & Load Performance
- **Network Footprint**: Combining all static styling into a single global stylesheet (`tailwind.css` + `dashboard.css`) reduces parallel HTTP roundtrips.
- **Resource Loading**: Modern `defer`/`async` scripts are used for javascript loading, ensuring that the DOM parser is not blocked.
- **Image Optimization**: The One logo (`logo.jpg`) is compressed and optimized for fast display in the navigation headers.
