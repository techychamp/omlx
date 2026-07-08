import SwiftUI

struct DeveloperStudioScreen: View {
    @State private var viewModel: DeveloperToolsViewModel
    @Environment(\.omlxTheme) private var theme

    init(services: AppServices) {
        _viewModel = State(initialValue: DeveloperToolsViewModel(services: services))
    }

    var body: some View {
        VStack(spacing: 0) {
            // Toolbar
            HStack {
                Text("Developer Studio")
                    .font(.headline)
                Spacer()
                Button(action: { viewModel.clearHistory() }) {
                    Image(systemName: "trash")
                }
                .buttonStyle(.plain)
                .help("Clear History")
            }
            .padding()
            .background(theme.windowBg)

            Divider()

            // Tab Picker
            Picker("Tab", selection: $viewModel.selectedTab) {
                ForEach(DeveloperStudioTab.allCases) { tab in
                    Text(tab.rawValue).tag(tab)
                }
            }
            .pickerStyle(.segmented)
            .padding()

            Divider()

            // Content
            Group {
                switch viewModel.selectedTab {
                case .apiExplorer:
                    APIExplorerView()
                case .requestInspector:
                    RequestInspectorView()
                case .responseInspector:
                    ResponseInspectorView()
                case .runtimeEvents:
                    RuntimeEventView(viewModel: viewModel)
                case .logExplorer:
                    LogExplorerView(viewModel: viewModel)
                case .traceViewer:
                    TraceViewerView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(theme.windowBg)
    }
}
