import SwiftUI

/// Main container for the Compiler Explorer workspace.
/// Uses a NavigationSplitView for a sidebar/detail layout.
struct CompilerWorkspaceView: View {
    @StateObject var viewModel: CompilerViewModel

    var body: some View {
        NavigationSplitView {
            // Sidebar: Explorer
            PlanningExplorerView(viewModel: viewModel)
                .navigationTitle("Explorer")
        } detail: {
            // Main content area
            VStack {
                Text("Compiler Workspace")
                    .font(.title)
                    .padding()

                if viewModel.isLoading {
                    ProgressView("Loading Compiler Data...")
                } else if let error = viewModel.errorMessage {
                    Text("Error: \(error)")
                        .foregroundColor(.red)
                } else {
                    ScrollView {
                        VStack(spacing: 20) {
                            CompilerPipelineView(viewModel: viewModel)
                                .frame(height: 100)

                            Divider()

                            ExecutionGraphView(viewModel: viewModel)
                                .frame(height: 300)

                            Divider()

                            HStack(alignment: .top, spacing: 20) {
                                OptimizationReportView(viewModel: viewModel)
                                    .frame(maxWidth: .infinity)

                                TimelineView(viewModel: viewModel)
                                    .frame(maxWidth: .infinity)
                            }

                            Divider()

                            ArtifactInspectorView(viewModel: viewModel)
                        }
                        .padding()
                    }
                }
            }
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button(action: {
                        Task {
                            await viewModel.load()
                        }
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
        .task {
            await viewModel.load()
        }
    }
}
