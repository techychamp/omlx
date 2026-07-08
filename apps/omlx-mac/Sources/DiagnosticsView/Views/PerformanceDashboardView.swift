import SwiftUI

struct PerformanceDashboardView: View {
    @StateObject private var viewModel: DiagnosticsViewModel

    init(diagnosticsService: DiagnosticsServiceProtocol) {
        _viewModel = StateObject(wrappedValue: DiagnosticsViewModel(diagnosticsService: diagnosticsService))
    }

    var body: some View {
        NavigationView {
            List {
                NavigationLink(destination: RuntimeMetricsView(viewModel: viewModel)) {
                    Label("Runtime Metrics", systemImage: "timer")
                }
                NavigationLink(destination: AppleMetricsView(viewModel: viewModel)) {
                    Label("Apple Silicon", systemImage: "cpu")
                }
                NavigationLink(destination: BenchmarkCenterView(viewModel: viewModel)) {
                    Label("Benchmark Center", systemImage: "chart.bar")
                }
                NavigationLink(destination: ExecutionTimelineView(viewModel: viewModel)) {
                    Label("Execution Timeline", systemImage: "clock")
                }
                NavigationLink(destination: ResourceDashboardView(viewModel: viewModel)) {
                    Label("Resource Dashboard", systemImage: "memorychip")
                }
                NavigationLink(destination: DiagnosticsExplorerView(viewModel: viewModel)) {
                    Label("Diagnostics Explorer", systemImage: "magnifyingglass")
                }
            }
            .listStyle(SidebarListStyle())
            .navigationTitle("Performance")

            Text("Select a diagnostics category")
                .foregroundColor(.secondary)
        }
        .onAppear {
            Task {
                await viewModel.fetchAll()
            }
        }
    }
}
