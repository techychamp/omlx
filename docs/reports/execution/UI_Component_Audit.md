# UI Component Audit

- Buttons: Found multiple instances of `bg-neutral-900`, `bg-white`, etc. Need to migrate to primary/secondary/ghost.
- Inputs: Found standard text, password, select inputs using utility borders.
- Navigation: Sidebar/Navbar present in dashboard.html and _navbar.html.
- Status: Badges use `bg-green-50`, `bg-amber-50`, etc. Needs mapping to success/warning tokens.
- Cards: Model cards and runtime cards present in _models.html, _status.html.
- Tables: Found in _bench.html.
- Modals: Settings and mirror modals use fixed backgrounds.
