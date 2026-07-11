import SwiftUI

struct TraceViewerView: View {
    let viewModel: DeveloperToolsViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack(spacing: 20) {
            Text("Request Lifecycle Trace")
                .font(.headline)

            VStack(alignment: .leading, spacing: 10) {
                ForEach(Array(viewModel.traceSteps.enumerated()), id: \.element.id) { index, step in
                    TraceStep(step: step)
                    if index < viewModel.traceSteps.count - 1 {
                        TraceArrow()
                    }
                }
            }
            .padding()
            .background(theme.groupBg)
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(theme.groupBorder, lineWidth: 1)
            )

            Spacer()
        }
        .padding()
    }
}

private struct TraceStep: View {
    let step: DeveloperTraceStep
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        HStack(alignment: .top, spacing: 8) {
            Image(systemName: step.icon)
                .frame(width: 24)
                .foregroundColor(theme.text)
            VStack(alignment: .leading, spacing: 2) {
                HStack {
                    Text(step.name)
                        .font(.body)
                        .foregroundColor(theme.text)
                    Text(step.status.rawValue)
                        .font(.caption.weight(.semibold))
                        .foregroundColor(color(for: step.status))
                }
                if let detail = step.detail, !detail.isEmpty {
                    Text(detail)
                        .font(.caption)
                        .foregroundColor(theme.textSecondary)
                        .lineLimit(2)
                }
            }
            Spacer()
        }
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
