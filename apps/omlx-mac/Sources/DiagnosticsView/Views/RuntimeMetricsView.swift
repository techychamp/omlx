import SwiftUI

struct RuntimeMetricsView: View {
    @ObservedObject var viewModel: DiagnosticsViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Runtime Metrics")
                .font(.largeTitle)
                .bold()

            if viewModel.isLoading {
                ProgressView("Loading...")
            } else if let error = viewModel.error {
                Text("Error: \(error.localizedDescription)").foregroundColor(.red)
            } else if let metrics = viewModel.executionMetrics {
                VStack(alignment: .leading, spacing: 10) {
                    MetricRow(label: "API Version", value: metrics.apiVersion ?? "N/A")
                    MetricRow(label: "Prompt Tokens", value: "\(metrics.promptTokens)")
                    MetricRow(label: "Completion Tokens", value: "\(metrics.completionTokens)")
                    MetricRow(label: "Total Tokens", value: "\(metrics.totalTokens)")
                }
                .padding()
                .background(Color(NSColor.controlBackgroundColor))
                .cornerRadius(10)
            } else {
                Text("No data available")
            }
            Spacer()
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }
}
