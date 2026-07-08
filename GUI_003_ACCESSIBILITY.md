# GUI-003 Accessibility Guide

## Accessibility Considerations
The Workspace was designed keeping accessibility top of mind:

1. **Dynamic Type Support:**
   - Fonts use `.omlxText()` with relative sizing, meaning they scale natively with user preferences.
   - Conversation bubbles and inputs adapt their padding to accommodate larger text.

2. **Contrast & Themes:**
   - The UI adheres to high-contrast themes via the `@Environment(\.omlxTheme)`.
   - Distinct backgrounds separate system UI (`windowBg`) from user-focused workspaces (`groupBg`).

3. **Keyboard Navigation:**
   - The `PromptComposer` captures `onSubmit` explicitly to map the Enter key to sending messages without requiring pointer clicks.

4. **Screen Reader (VoiceOver) Integration:**
   - The standard SwiftUI `List` used in `SessionSidebar` automatically supports VoiceOver navigation. Additional contextual actions (deleting sessions) use standard accessible context menus.
   - Status indicators have associated textual readouts (e.g., "Runtime Online").
   - Explicit labels, hints, and combine groupings were added across `RuntimeStatusView`, `PromptComposer`, `ConversationView`, and `SessionSidebar`.
