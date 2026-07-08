# GUI-008 Settings

## Preferences Scene
Settings are managed in a standard macOS `Settings` scene, accessible via `⌘,` or the application menu.

## Available Categories
1. **Appearance:** Toggles between Light, Dark, and System appearance.
2. **Editor:** Configurations for the workspace prompt and syntax highlighting.
3. **Developer:** Advanced toggles for logging and developer tools.
4. **Window:** Preferences for sidebar and inspector behaviors.
5. **Accessibility:** Preferences for reduced motion and high contrast adjustments.

Settings are persisted locally via `UserDefaults` (using `@AppStorage`). They do not affect remote server states.
