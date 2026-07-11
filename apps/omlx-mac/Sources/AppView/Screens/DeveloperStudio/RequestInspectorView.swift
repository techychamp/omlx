import SwiftUI

struct RequestInspectorView: View {
    let viewModel: DeveloperToolsViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Request Inspector")
                .font(.headline)

            if viewModel.endpointEvents.isEmpty {
                Text("No request data captured yet.")
                    .foregroundColor(theme.textTertiary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .center)
            } else {
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        ForEach(viewModel.endpointEvents) { event in
                            VStack(alignment: .leading, spacing: 6) {
                                HStack {
                                    Text(event.method)
                                        .font(.system(.caption, design: .monospaced).weight(.semibold))
                                        .padding(.horizontal, 6)
                                        .padding(.vertical, 2)
                                        .background(theme.codeBg)
                                        .clipShape(RoundedRectangle(cornerRadius: 4))
                                    Text(event.path)
                                        .font(.system(.body, design: .monospaced))
                                    Spacer()
                                    Text(event.status.rawValue)
                                        .font(.caption.weight(.semibold))
                                        .foregroundColor(color(for: event.status))
                                }
                                if let duration = event.durationMs {
                                    Text("\(duration) ms")
                                        .font(.caption)
                                        .foregroundColor(theme.textSecondary)
                                }
                            }
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

    private func color(for status: DeveloperTraceStatus) -> Color {
        switch status {
        case .pending: return theme.textTertiary
        case .running: return .blue
        case .completed: return .green
        case .failed: return .red
        }
    }
}
