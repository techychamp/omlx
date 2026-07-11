# RUN-005 Known Limitations

- Duplicate View-specific structs (e.g. `UploadRow`, `StatusChip`) exist in individual screens, but they are localized and `private`/internal, so no architectural boundary is crossed. 
- Some mock DTO responses use fallback values for previews where strict JSON structure parsing is enforced.
