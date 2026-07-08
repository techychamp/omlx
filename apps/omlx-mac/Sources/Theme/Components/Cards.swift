import SwiftUI

struct MetricCard: View {
    @Environment(\.omlxTheme) private var theme
    var title: String
    var value: String
    var icon: String? = nil
    var iconColor: Color? = nil
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                if let icon = icon {
                    Image(systemName: icon)
                        .foregroundColor(iconColor ?? theme.textSecondary)
                }
                Text(title)
                    .font(.subheadline)
                    .foregroundColor(theme.textSecondary)
            }
            
            Text(value)
                .font(.title2)
                .fontWeight(.semibold)
                .foregroundColor(theme.text)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(theme.groupBg) // assuming groupBg exists
        .cornerRadius(8)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(value)")
    }
}

struct PlaceholderCard: View {
    @Environment(\.omlxTheme) private var theme
    var title: String
    var message: String = "Unavailable via current Runtime API"
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .foregroundColor(theme.text)
            
            HStack {
                Image(systemName: "lock.fill")
                    .foregroundColor(theme.textTertiary)
                Text(message)
                    .font(.subheadline)
                    .foregroundColor(theme.textSecondary)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(theme.groupBg) // will fall back to groupBg if cardBg doesn't exist. wait!
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(theme.groupBorder, style: StrokeStyle(lineWidth: 1, dash: [4]))
        )
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(title): \(message)")
    }
}
