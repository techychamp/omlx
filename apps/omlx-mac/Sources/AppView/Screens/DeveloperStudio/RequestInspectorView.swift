import SwiftUI

struct RequestInspectorView: View {
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack {
            Text("Request Inspector")
                .font(.headline)
            Text("Displays outgoing request, serialized DTO, headers, endpoint, timestamps, duration.")
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
