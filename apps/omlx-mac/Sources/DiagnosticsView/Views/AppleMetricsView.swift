import SwiftUI

struct AppleMetricsView: View {
    @ObservedObject var viewModel: DiagnosticsViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Apple Silicon Metrics")
                .font(.largeTitle)
                .bold()

            if viewModel.isLoading {
                ProgressView("Loading...")
            } else if let error = viewModel.error {
                Text("Error: \(error.localizedDescription)").foregroundColor(.red)
            } else if let metrics = viewModel.appleMetrics {
                VStack(alignment: .leading, spacing: 10) {
                    MetricRow(label: "API Version", value: metrics.apiVersion ?? "N/A")
                    MetricRow(label: "Memory Used", value: "\(metrics.memoryUsed / (1024 * 1024)) MB")
                    MetricRow(label: "ANE Utilization", value: String(format: "%.1f %%", metrics.aneUtilization * 100))
                    MetricRow(label: "GPU Utilization", value: String(format: "%.1f %%", metrics.gpuUtilization * 100))
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

struct MetricRow: View {
    let label: String
    let value: String

    var body: some View {
        HStack {
            Text(label).bold()
            Spacer()
            Text(value)
        }
    }
}
