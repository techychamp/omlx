import SwiftUI

@MainActor
final class WindowStateManager: ObservableObject {
    @AppStorage("AppSelectedWorkspace") var selectedWorkspace: String = "status"
    @AppStorage("AppSelectedSession") var selectedSession: String = ""
    @Published var sidebarVisibility: NavigationSplitViewVisibility = .automatic
    @AppStorage("AppInspectorVisibility") var inspectorVisibility: Bool = false
    
    // Note: SwiftUI automatically persists window frames for us in macOS if we use the default
    // standard Scene configurations. If we need to explicitly track it, we can use 
    // GeometryReader + onChange, but usually macOS handles window sizing per Scene.
    
    // Provide a safe way to set selected workspace (AppSection rawValue)
    func navigate(to section: String) {
        selectedWorkspace = section
    }
}
