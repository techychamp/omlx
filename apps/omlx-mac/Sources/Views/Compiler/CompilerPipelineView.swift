import SwiftUI

struct CompilerPipelineView: View {
    @ObservedObject var viewModel: CompilerViewModel
    @Environment(\.omlxTheme) private var theme

    let stages = [
        "Planning",
        "Logical IR",
        "Compiler Passes",
        "Physical IR",
        "Backend Translation",
        "Execution Graph"
    ]

    var body: some View {
        VStack(alignment: .leading) {
            Text("Compiler Pipeline")
                .font(.headline)

            Text("Limitation: Live stage tracking is unavailable in v1 API. Showing static pipeline representation.")
                .font(.caption)
                .foregroundColor(.secondary)

            HStack(spacing: 0) {
                ForEach(0..<stages.count, id: \.self) { index in
                    VStack {
                        Circle()
                            .fill(Color.blue.opacity(0.5))
                            .frame(width: 30, height: 30)
                            .overlay(
                                Text("\(index + 1)")
                                    .foregroundColor(.white)
                                    .font(.caption)
                            )

                        Text(stages[index])
                            .font(.caption2)
                            .multilineTextAlignment(.center)
                            .frame(width: 80)
                    }

                    if index < stages.count - 1 {
                        Rectangle()
                            .fill(Color(theme.groupBorder))
                            .frame(height: 2)
                            .frame(maxWidth: .infinity)
                            .padding(.bottom, 20) // align with circles
                    }
                }
            }
            .padding(.top, 10)
        }
    }
}
