import SwiftUI

struct TimelineView: View {
    @ObservedObject var viewModel: CompilerViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack(alignment: .leading) {
            Text("Execution Timeline")
                .font(.headline)

            Text("Limitation: Execution timeline data is unavailable in the frozen v1 GUI-002 API.")
                .font(.caption)
                .foregroundColor(.secondary)

            List {
                Text("No timeline data available.")
                    .foregroundColor(.secondary)
            }
            .listStyle(.plain)
            .frame(height: 150)
            .background(Color(theme.groupBorder))
            .cornerRadius(8)
        }
    }
}
