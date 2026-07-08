import SwiftUI

struct SessionManagementView: View {
    let sessions: [SessionInfo]
    
    @Environment(\.omlxTheme) private var theme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Session Management")
                .font(.omlxText(16, weight: .semibold))
                .foregroundStyle(theme.text)
                .accessibilityAddTraits(.isHeader)
            
            if sessions.isEmpty {
                Text("No sessions active.")
                    .font(.omlxText(13))
                    .foregroundStyle(theme.textSecondary)
                    .accessibilityLabel("No active sessions")
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Session Count: \(sessions.count)")
                        .font(.omlxText(13))
                        .foregroundStyle(theme.textSecondary)
                        .accessibilityLabel("Total \(sessions.count) active sessions")
                    
                    ForEach(sessions, id: \.sessionId) { session in
                        HStack {
                            Text(session.sessionId)
                                .font(.omlxText(13, weight: .medium))
                                .foregroundStyle(theme.text)
                            Spacer()
                            Text(session.createdAt.formatted())
                                .font(.omlxText(11))
                                .foregroundStyle(theme.textTertiary)
                        }
                        .padding(.vertical, 4)
                        .accessibilityElement(children: .combine)
                        .accessibilityLabel("Session \(session.sessionId) created at \(session.createdAt.formatted())")
                    }
                }
            }
            
            Divider()
            
            Text("Feature unavailable in current Runtime API (Rename, Delete, Merge, Export, Archive)")
                .font(.omlxText(12, weight: .medium))
                .foregroundStyle(theme.textTertiary)
                .padding(.top, 8)
                .accessibilityLabel("Session editing features are unavailable in the current Runtime API")
        }
        .padding()
        .background(theme.groupBg)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(theme.groupBorder, lineWidth: 1)
        )
    }
}
