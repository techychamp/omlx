import SwiftUI

struct BenchmarkCenterView: View {
    @ObservedObject var viewModel: DiagnosticsViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Benchmark Center")
                .font(.largeTitle)
                .bold()

            if viewModel.isLoading {
                ProgressView("Loading...")
            } else if let error = viewModel.error(for: .benchmarks) {
                Text("Error: \(error.omlxDescription)").foregroundColor(.red)
            } else if let report = viewModel.benchmarkReport {
                VStack(alignment: .leading, spacing: 10) {
                    MetricRow(label: "API Version", value: report.apiVersion ?? "N/A")
                    MetricRow(label: "Throughput", value: String(format: "%.2f", report.throughput))
                    MetricRow(label: "Tokens / Sec", value: String(format: "%.2f", report.tokensPerSecond))
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
