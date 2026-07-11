import SwiftUI

struct DiagnosticsExplorerView: View {
    @ObservedObject var viewModel: DiagnosticsViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Diagnostics Explorer")
                .font(.largeTitle)
                .bold()

            if viewModel.isLoading {
                ProgressView("Loading...")
            } else if let error = viewModel.error(for: .explorer) {
                Text("Error: \(error.omlxDescription)").foregroundColor(.red)
            } else if let inspection = viewModel.compilerInspection {
                VStack(alignment: .leading, spacing: 10) {
                    MetricRow(label: "API Version", value: inspection.apiVersion ?? "N/A")
                    MetricRow(label: "Compiler Version", value: inspection.compilerVersion)
                    MetricRow(label: "Graph Status", value: inspection.graphStatus)
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
