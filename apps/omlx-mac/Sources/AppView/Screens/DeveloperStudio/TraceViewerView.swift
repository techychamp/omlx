import SwiftUI

struct TraceViewerView: View {
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack(spacing: 20) {
            Text("Request Lifecycle Trace")
                .font(.headline)

            VStack(alignment: .leading, spacing: 10) {
                TraceStep(name: "View", icon: "macwindow")
                TraceArrow()
                TraceStep(name: "ViewModel", icon: "brain")
                TraceArrow()
                TraceStep(name: "Service", icon: "network")
                TraceArrow()
                TraceStep(name: "OMLXClient", icon: "globe")
                TraceArrow()
                TraceStep(name: "Runtime", icon: "cpu")
                TraceArrow()
                TraceStep(name: "Compiler", icon: "gearshape.2")
                TraceArrow()
                TraceStep(name: "Execution", icon: "bolt.fill")
                TraceArrow()
                TraceStep(name: "Response", icon: "arrow.uturn.left")
            }
            .padding()
            .background(theme.groupBg)
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(theme.groupBorder, lineWidth: 1)
            )

            Spacer()
        }
        .padding()
    }
}

private struct TraceStep: View {
    let name: String
    let icon: String
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        HStack {
            Image(systemName: icon)
                .frame(width: 24)
                .foregroundColor(theme.textPrimary)
            Text(name)
                .font(.body)
                .foregroundColor(theme.textPrimary)
            Spacer()
        }
    }
}

private struct TraceArrow: View {
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        HStack {
            Image(systemName: "arrow.down")
                .frame(width: 24)
                .foregroundColor(theme.textTertiary)
            Spacer()
        }
    }
}
