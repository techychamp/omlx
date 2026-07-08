import SwiftUI

struct LogExplorerView: View {
    let viewModel: DeveloperToolsViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if let compiler = viewModel.compilerInspection {
                    SectionHeader(title: "Compiler Diagnostics")
                    VStack(alignment: .leading) {
                        Text("Version: \(compiler.compilerVersion)")
                        Text("Status: \(compiler.graphStatus)")
                    }
                    .padding()
                    .background(theme.groupBg)
                    .cornerRadius(8)
                }

                if let exec = viewModel.executionMetrics {
                    SectionHeader(title: "Execution Metrics")
                    VStack(alignment: .leading) {
                        Text("Prompt Tokens: \(exec.promptTokens)")
                        Text("Completion Tokens: \(exec.completionTokens)")
                        Text("Total Tokens: \(exec.totalTokens)")
                    }
                    .padding()
                    .background(theme.groupBg)
                    .cornerRadius(8)
                }

                if let apple = viewModel.appleMetrics {
                    SectionHeader(title: "Apple Silicon Metrics")
                    VStack(alignment: .leading) {
                        Text("Memory Used: \(apple.memoryUsed) bytes")
                        Text("ANE Utilization: \(String(format: "%.1f", apple.aneUtilization))%")
                        Text("GPU Utilization: \(String(format: "%.1f", apple.gpuUtilization))%")
                    }
                    .padding()
                    .background(theme.groupBg)
                    .cornerRadius(8)
                }

                if viewModel.compilerInspection == nil && viewModel.executionMetrics == nil && viewModel.appleMetrics == nil {
                    Text("No diagnostics data available.")
                        .foregroundColor(theme.textTertiary)
                        .padding()
                }
            }
            .padding()
        }
        .task {
            await viewModel.refreshData()
        }
    }
}
