import SwiftUI

struct ArtifactInspectorView: View {
    @ObservedObject var viewModel: CompilerViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Artifact Inspector")
                .font(.headline)

            Text("Limitation: Detailed artifact metadata is not exposed in the frozen v1 API.")
                .font(.caption)
                .foregroundColor(.secondary)

            Form {
                Section(header: Text("Compiler Inspection Details")) {
                    if let inspection = viewModel.compilerInspection {
                        LabeledContent("Compiler Version", value: inspection.compilerVersion)
                        LabeledContent("Graph Status", value: inspection.graphStatus)
                        if let apiVersion = inspection.apiVersion {
                            LabeledContent("API Version", value: apiVersion)
                        }
                    } else {
                        Text("No data selected/available.")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .formStyle(.grouped)
            .frame(height: 200)
        }
    }
}
