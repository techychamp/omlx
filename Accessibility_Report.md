# Accessibility Report

This report documents the accessibility audit for the One Admin Dashboard interface.

## 1. Semantic Markup
- All headings follow a clean hierarchical tree (`<h1>` through `<h5>`), ensuring page structures are legible for screen readers.
- Modern HTML5 tags (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`) are strictly used across the main template and sub-panels.
- Form inputs have corresponding descriptive `<label>` tags to guarantee full VoiceOver clarity.

## 2. Color Contrast (WCAG 2.1 AA)
- The dark mode theme uses high-contrast text shades (`#F9FAFB` on Space Black `#030712`) providing a ratio above **7:1**.
- The light mode uses soft grays (`#374151` on Off-White/Pearl `#F3F4F6`), achieving a ratio above **4.5:1**.
- Hover states utilize smooth scaling transitions and opacity adjustments to clearly signal focused controls without relying solely on color indicators.

## 3. Keyboard & Screen Reader Navigation
- Interactive controls (buttons, links, inputs) have a logical tab order.
- Active states have visual focus rings matching the blue/violet accent outlines.
- Alt text and aria labels are correctly populated for critical UI controls.
