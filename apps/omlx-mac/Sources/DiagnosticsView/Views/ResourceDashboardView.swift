import SwiftUI

struct ResourceDashboardView: View {
    @ObservedObject var viewModel: DiagnosticsViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Resource Dashboard")
                .font(.largeTitle)
                .bold()

            if let metrics = viewModel.appleMetrics {
                 VStack(alignment: .leading, spacing: 10) {
                     MetricRow(label: "Memory Used", value: "\(metrics.memoryUsed / (1024 * 1024)) MB")
                     MetricRow(label: "GPU Utilization", value: String(format: "%.1f %%", metrics.gpuUtilization * 100))
                 }
                 .padding()
                 .background(Color(NSColor.controlBackgroundColor))
                 .cornerRadius(10)
             } else {
                 Text("No resource data available")
             }

            Spacer()
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }
}
