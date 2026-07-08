import SwiftUI

struct ExecutionGraphView: View {
    @ObservedObject var viewModel: CompilerViewModel
    @Environment(\.omlxTheme) private var theme
    @State private var scale: CGFloat = 1.0
    @State private var offset: CGSize = .zero

    var body: some View {
        VStack(alignment: .leading) {
            Text("Execution Graph Viewer")
                .font(.headline)

            Text("Limitation: Detailed Execution Graph data is not exposed in the frozen v1 API.")
                .font(.caption)
                .foregroundColor(.secondary)

            GeometryReader { geometry in
                ZStack {
                    Color(theme.groupBorder)
                        .cornerRadius(8)

                    VStack(spacing: 40) {
                        GraphNodePlaceholder(title: "Input Node")
                        GraphEdgePlaceholder()
                        GraphNodePlaceholder(title: "Processing Node")
                        GraphEdgePlaceholder()
                        GraphNodePlaceholder(title: "Output Node")
                    }
                    .scaleEffect(scale)
                    .offset(offset)
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                offset = value.translation
                            }
                    )
                }
                .clipped()
            }

            // Zoom controls
            HStack {
                Button(action: { scale = max(0.5, scale - 0.1) }) {
                    Image(systemName: "minus.magnifyingglass")
                }
                Text("\(Int(scale * 100))%")
                    .frame(width: 50)
                Button(action: { scale = min(3.0, scale + 0.1) }) {
                    Image(systemName: "plus.magnifyingglass")
                }
                Spacer()
                Button("Reset") {
                    scale = 1.0
                    offset = .zero
                }
            }
            .padding(.top, 8)
        }
    }
}

struct GraphNodePlaceholder: View {
    let title: String

    var body: some View {
        Text(title)
            .padding()
            .background(Color.blue.opacity(0.2))
            .cornerRadius(8)
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color.blue, lineWidth: 1)
            )
    }
}

struct GraphEdgePlaceholder: View {
    @Environment(\.omlxTheme) private var theme
    
    var body: some View {
        Rectangle()
            .fill(Color(theme.groupBorder))
            .frame(width: 2, height: 40)
    }
}
