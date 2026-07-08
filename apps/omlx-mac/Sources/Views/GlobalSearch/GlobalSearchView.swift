import SwiftUI

struct GlobalSearchView: View {
    @Environment(AppServices.self) private var services
    @Environment(\.omlxTheme) private var theme
    
    @StateObject private var viewModel: GlobalSearchViewModel
    @EnvironmentObject private var shortcutManager: KeyboardShortcutManager
    @EnvironmentObject private var windowStateManager: WindowStateManager
    
    init(services: AppServices) {
        _viewModel = StateObject(wrappedValue: GlobalSearchViewModel(services: services))
    }
    
    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(theme.textSecondary)
                
                TextField("Search Workspace, Models, Sessions...", text: $viewModel.query)
                    .textFieldStyle(.plain)
                    .font(.title3)
                    .onChange(of: viewModel.query) { _ in
                        viewModel.performSearch()
                    }
                
                if viewModel.isSearching {
                    ProgressView()
                        .controlSize(.small)
                }
            }
            .padding()
            
            Divider()
                .background(theme.groupBorder)
            
            List {
                ForEach(viewModel.results) { result in
                    Button(action: {
                        shortcutManager.showGlobalSearch = false
                        windowStateManager.navigate(to: result.targetSection.rawValue)
                    }) {
                        HStack {
                            VStack(alignment: .leading) {
                                Text(result.title)
                                    .font(.body)
                                    .foregroundColor(theme.text)
                                if let sub = result.subtitle {
                                    Text(sub)
                                        .font(.caption)
                                        .foregroundColor(theme.textSecondary)
                                }
                            }
                            Spacer()
                            Text(result.type.rawValue)
                                .font(.caption2)
                                .padding(4)
                                .background(theme.groupBg)
                                .cornerRadius(4)
                                .foregroundColor(theme.textSecondary)
                        }
                    }
                    .buttonStyle(.plain)
                    .padding(.vertical, 4)
                }
            }
            .listStyle(.plain)
        }
        .frame(width: 500, height: 400)
        .background(theme.windowBg)
        .cornerRadius(12)
        .shadow(radius: 20)
        .onAppear {
            viewModel.performSearch() // load default nav results
        }
    }
}
