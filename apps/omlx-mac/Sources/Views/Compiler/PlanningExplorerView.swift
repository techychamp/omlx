import SwiftUI

struct PlanningExplorerView: View {
    @ObservedObject var viewModel: CompilerViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Planning Explorer")
                .font(.headline)

            Text("Note: Detailed PlanningBundle data is not available via the frozen v1 GUI-002 API.")
                .font(.caption)
                .foregroundColor(.secondary)

            Divider()

            if let inspection = viewModel.compilerInspection {
                Text("Compiler Version: \(inspection.compilerVersion)")
                Text("Status: \(inspection.graphStatus)")
            } else {
                Text("No data loaded.")
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
        .padding()
    }
}
