import SwiftUI

struct LoadingView: View {
    @Environment(\.omlxTheme) private var theme
    var title: String = "Loading..."
    
    var body: some View {
        VStack(spacing: 12) {
            ProgressView()
                .controlSize(.regular)
            Text(title)
                .font(.body)
                .foregroundColor(theme.textSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(title)
    }
}

struct EmptyStateView: View {
    @Environment(\.omlxTheme) private var theme
    var icon: String
    var title: String
    var description: String
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 48))
                .foregroundColor(theme.textTertiary)
            Text(title)
                .font(.headline)
                .foregroundColor(theme.text)
            Text(description)
                .font(.subheadline)
                .foregroundColor(theme.textSecondary)
                .multilineTextAlignment(.center)
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title), \(description)")
    }
}

struct ErrorStateView: View {
    @Environment(\.omlxTheme) private var theme
    var errorMessage: String
    var retryAction: (() -> Void)?
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 48))
                .foregroundColor(theme.redDot) // using redDot instead of alertError since alertError might not exist
            
            Text("Something went wrong")
                .font(.headline)
                .foregroundColor(theme.text)
            
            Text(errorMessage)
                .font(.subheadline)
                .foregroundColor(theme.textSecondary)
                .multilineTextAlignment(.center)
            
            if let retryAction = retryAction {
                Button("Retry", action: retryAction)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Error: \(errorMessage)")
    }
}
