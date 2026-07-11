import SwiftUI

struct PreferencesView: View {
    var body: some View {
        TabView {
            AppearanceSettingsView()
                .tabItem {
                    Label("Appearance", systemImage: "paintpalette")
                }
            
            EditorSettingsView()
                .tabItem {
                    Label("Editor", systemImage: "character.cursor.ibeam")
                }
            
            DeveloperSettingsView()
                .tabItem {
                    Label("Developer", systemImage: "hammer")
                }
            
            WindowSettingsView()
                .tabItem {
                    Label("Window", systemImage: "macwindow")
                }
            
            AccessibilitySettingsView()
                .tabItem {
                    Label("Accessibility", systemImage: "accessibility")
                }
        }
        .padding()
        .frame(width: 500, height: 400)
    }
}

struct AppearanceSettingsView: View {
    @EnvironmentObject var appearanceManager: AppearanceManager
    
    var body: some View {
        Form {
            Picker("Theme", selection: $appearanceManager.appearanceMode) {
                ForEach(AppearanceManager.AppearanceMode.allCases) { mode in
                    Text(mode.title).tag(mode)
                }
            }
            .pickerStyle(.radioGroup)
        }
        .padding()
    }
}

struct EditorSettingsView: View {
    var body: some View {
        VStack {
            Text("Editor settings will go here (font size, wrapping, etc.)")
                .foregroundColor(Color.secondary)
        }
    }
}

struct DeveloperSettingsView: View {
    var body: some View {
        VStack {
            Text("Developer settings will go here (debug logs, experimental features)")
                .foregroundColor(Color.secondary)
        }
    }
}

struct WindowSettingsView: View {
    var body: some View {
        VStack {
            Text("Window behavior settings (translucency, standard sizing)")
                .foregroundColor(Color.secondary)
        }
    }
}

struct AccessibilitySettingsView: View {
    var body: some View {
        VStack {
            Text("Accessibility settings (reduce motion, high contrast)")
                .foregroundColor(Color.secondary)
        }
    }
}
