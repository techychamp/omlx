import SwiftUI

struct SessionSidebar: View {
    @Bindable var vm: SessionViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Sessions")
                    .font(.omlxText(13, weight: .semibold))
                    .foregroundColor(theme.textSecondary)
                    .accessibilityHidden(true)
                Spacer()
                Button(action: {
                    vm.createNewSession()
                }) {
                    Image(systemName: "square.and.pencil")
                }
                .buttonStyle(.plain)
                .foregroundColor(theme.textSecondary)
                .help("New Session")
                .accessibilityLabel("New Session")
                .accessibilityHint("Creates a new blank chat session.")
                .accessibilityIdentifier("NewSessionButton")
            }
            .padding()
            .accessibilityElement(children: .contain)
            .accessibilityLabel("Session Controls")

            Divider()
                .background(theme.groupBorder)

            if vm.sessions.isEmpty {
                VStack {
                    Spacer()
                    Text("No sessions found")
                        .font(.omlxText(12))
                        .foregroundColor(theme.textTertiary)
                    Spacer()
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("No past sessions found")
            } else {
                List(selection: $vm.activeSessionId) {
                    ForEach(vm.sessions, id: \.sessionId) { session in
                        Text(session.sessionId.prefix(8))
                            .font(.omlxText(13))
                            .tag(session.sessionId)
                            .accessibilityLabel("Session \(session.sessionId.prefix(8))")
                            .accessibilityHint("Select to resume this session.")
                            .contextMenu {
                                Button(role: .destructive) {
                                    vm.deleteSession(session.sessionId)
                                } label: {
                                    Label("Delete Session", systemImage: "trash")
                                }
                                .accessibilityLabel("Delete Session")
                            }
                    }
                }
                .listStyle(.sidebar)
                .accessibilityIdentifier("SessionList")
            }
        }
        .accessibilityIdentifier("SessionSidebar")
    }
}
