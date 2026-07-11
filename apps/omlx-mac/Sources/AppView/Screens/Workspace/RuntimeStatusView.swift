import SwiftUI

struct RuntimeStatusView: View {
    @Environment(AppServices.self) private var services
    @Environment(\.omlxTheme) private var theme

    @State private var status: RuntimeStatus?

    var body: some View {
        HStack {
            Circle()
                .fill(status != nil ? Color.green : Color.red)
                .frame(width: 8, height: 8)

            Text(status != nil ? "Runtime Online" : "Runtime Offline")
                .font(.omlxText(11, weight: .medium))
                .foregroundColor(theme.textSecondary)
                .accessibilityLabel("Runtime status: \(status != nil ? "Online" : "Offline")")

            if let version = status?.version {
                Text("v\(version)")
                    .font(.omlxText(11))
                    .foregroundColor(theme.textTertiary)
                    .accessibilityLabel("Runtime version \(version)")
            }

            Spacer()
        }
        .onAppear {
            Task { await fetchStatus() }
        }
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier("RuntimeStatusView")
    }

    private func fetchStatus() async {
        do {
            status = try await services.platformService.getStatus()
        } catch {
            status = nil
        }
    }
}
