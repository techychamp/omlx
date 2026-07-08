import SwiftUI

struct ResponseInspectorView: View {
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack {
            Text("Response Inspector")
                .font(.headline)
            Text("Displays decoded response, response metadata, execution duration, runtime status, diagnostics references.")
                .font(.subheadline)
                .foregroundColor(theme.textSecondary)

            Spacer()
            Text("No data available.")
                .foregroundColor(theme.textTertiary)
            Spacer()
        }
        .padding()
    }
}
