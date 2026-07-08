import SwiftUI

@MainActor
final class AppearanceManager: ObservableObject {
    @AppStorage("AppAppearanceMode") var appearanceMode: AppearanceMode = .system {
        didSet {
            objectWillChange.send()
        }
    }
    
    enum AppearanceMode: String, CaseIterable, Identifiable {
        case system
        case light
        case dark
        
        var id: String { rawValue }
        
        var colorScheme: ColorScheme? {
            switch self {
            case .system: return nil
            case .light: return .light
            case .dark: return .dark
            }
        }
        
        var title: String {
            switch self {
            case .system: return String(localized: "appearance.system", defaultValue: "System")
            case .light: return String(localized: "appearance.light", defaultValue: "Light")
            case .dark: return String(localized: "appearance.dark", defaultValue: "Dark")
            }
        }
    }
}
