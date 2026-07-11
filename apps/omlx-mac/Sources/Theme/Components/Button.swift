import SwiftUI

struct OMLXButtonWrapper: View {
    let configuration: ButtonStyle.Configuration
    let kind: OMLXButtonStyle.Kind
    let size: OMLXButtonStyle.Size
    let theme: OMLXTheme
    let isEnabled: Bool
    let pageRole: OMLXPageRole
    
    @State private var isHovered = false
    
    var body: some View {
        let labelFont = OneDesign.Typography.omlxBody(.semibold)
        let hPad: CGFloat = size == .small ? OneDesign.Spacing.spacingS : OneDesign.Spacing.spacingM
        let vPad: CGFloat = size == .small ? OneDesign.Spacing.spacingXS : OneDesign.Spacing.spacingS
        
        let atmosphere = OneDesign.SemanticRoles.resolveAtmosphere(for: pageRole, isDark: theme.isDark)
        let activeAccent = atmosphere.accent
        
        configuration.label
            .font(labelFont)
            .padding(.horizontal, hPad)
            .padding(.vertical, vPad)
            .foregroundStyle(foreground)
            .background(background(activeAccent))
            .clipShape(RoundedRectangle(cornerRadius: OneDesign.Layout.controlRadius, style: .continuous))
            .overlay(border(activeAccent))
            .opacity(opacity)
            .omlxButtonInteractiveGlow(isHovered: isHovered && isEnabled, isPressed: configuration.isPressed && isEnabled, role: pageRole, isDark: theme.isDark)
            .onHover { hovering in
                isHovered = hovering
            }
    }
    
    private var opacity: Double {
        guard isEnabled else { return 0.45 }
        return 1.0
    }
    
    @ViewBuilder
    private func background(_ accentColor: Color) -> some View {
        switch kind {
        case .primary:
            accentColor
        case .destructive:
            theme.redDot
        case .normal:
            isHovered ? theme.selBg.opacity(0.4) : Color.clear
        case .plain:
            configuration.isPressed ? theme.hoverBg : Color.clear
        }
    }
    
    private var foreground: Color {
        switch kind {
        case .primary:
            return theme.accentText
        case .destructive:
            return .white
        case .normal:
            return theme.text
        case .plain:
            return theme.text
        }
    }
    
    @ViewBuilder
    private func border(_ accentColor: Color) -> some View {
        if kind == .normal {
            RoundedRectangle(cornerRadius: OneDesign.Layout.controlRadius, style: .continuous)
                .strokeBorder(theme.blueDot, lineWidth: 1.0)
        } else if kind == .primary {
            RoundedRectangle(cornerRadius: OneDesign.Layout.controlRadius, style: .continuous)
                .strokeBorder(accentColor.opacity(0.3), lineWidth: 0.5)
        }
    }
}

struct OMLXButtonStyle: ButtonStyle {
    enum Kind: Sendable { case primary, destructive, normal, plain }
    enum Size: Sendable { case small, regular }

    let kind: Kind
    let size: Size

    @Environment(\.omlxTheme) private var theme
    @Environment(\.isEnabled) private var isEnabled
    @Environment(\.omlxPageRole) private var pageRole

    func makeBody(configuration: Configuration) -> some View {
        OMLXButtonWrapper(
            configuration: configuration,
            kind: kind,
            size: size,
            theme: theme,
            isEnabled: isEnabled,
            pageRole: pageRole
        )
    }
}

extension ButtonStyle where Self == OMLXButtonStyle {
    static func omlx(
        _ kind: OMLXButtonStyle.Kind = .normal,
        size: OMLXButtonStyle.Size = .regular
    ) -> OMLXButtonStyle {
        OMLXButtonStyle(kind: kind, size: size)
    }
}
