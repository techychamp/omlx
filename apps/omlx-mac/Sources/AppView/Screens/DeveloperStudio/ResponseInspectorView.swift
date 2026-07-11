import SwiftUI

struct ResponseInspectorView: View {
    let viewModel: DeveloperToolsViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Response Inspector")
                .font(.headline)

            if viewModel.responseSummaries.isEmpty {
                Text("No decoded responses captured yet.")
                    .foregroundColor(theme.textTertiary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
            } else {
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        ForEach(Array(viewModel.responseSummaries.enumerated()), id: \.offset) { _, summary in
                            Text(summary)
                                .font(.system(.body, design: .monospaced))
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .padding(10)
                                .background(theme.groupBg)
                                .clipShape(RoundedRectangle(cornerRadius: 8))
                        }
                    }
                }
            }
        }
        .padding()
    }
}
