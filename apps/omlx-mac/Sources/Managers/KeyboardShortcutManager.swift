import SwiftUI
import Combine

@MainActor
final class KeyboardShortcutManager: ObservableObject {
    @Published var showGlobalSearch: Bool = false
    @Published var requestNewChat: Bool = false
    @Published var focusPrompt: Bool = false
    @Published var toggleSidebar: Bool = false
    
    // Allows any view to trigger global search, or commands from menu bar
    func openGlobalSearch() {
        showGlobalSearch = true
    }
}
