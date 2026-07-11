import SwiftUI

extension OneDesign {
    public enum Interaction {
        // Custom interactive view modifiers to apply across buttons/inputs
        public struct BorderGlowModifier: ViewModifier {
            let isFocused: Bool
            let hasValidation: Bool
            let role: OMLXPageRole
            let isDark: Bool
            
            public func body(content: Content) -> some View {
                let atmosphere = OneDesign.SemanticRoles.resolveAtmosphere(for: role, isDark: isDark)
                let surfaces = isDark ? OneDesign.Surfaces.dark : OneDesign.Surfaces.light
                
                let borderStrokeColor: Color = {
                    if hasValidation {
                        return isDark ? OneDesign.Colors.goldDark : OneDesign.Colors.goldLight
                    } else if isFocused {
                        return atmosphere.accent
                    } else {
                        return surfaces.border
                    }
                }()
                
                let shadowColor: Color = {
                    if hasValidation {
                        return (isDark ? OneDesign.Colors.goldDark : OneDesign.Colors.goldLight).opacity(0.2)
                    } else if isFocused {
                        return atmosphere.glowColor
                    } else {
                        return .clear
                    }
                }()
                
                content
                    .overlay(
                        RoundedRectangle(cornerRadius: OneDesign.Layout.controlRadius, style: .continuous)
                            .stroke(borderStrokeColor, lineWidth: isFocused || hasValidation ? 1.5 : 0.8)
                    )
                    .shadow(color: shadowColor, radius: isFocused || hasValidation ? 3 : 0, x: 0, y: 0)
                    .animation(OneDesign.Motion.fast, value: isFocused)
                    .animation(OneDesign.Motion.fast, value: hasValidation)
            }
        }
        
        public struct ButtonInteractiveGlowModifier: ViewModifier {
            let isHovered: Bool
            let isPressed: Bool
            let role: OMLXPageRole
            let isDark: Bool
            
            public func body(content: Content) -> some View {
                let atmosphere = OneDesign.SemanticRoles.resolveAtmosphere(for: role, isDark: isDark)
                let scale: CGFloat = isPressed ? 0.98 : (isHovered ? 1.01 : 1.0)
                let glowRadius: CGFloat = isPressed ? 2 : (isHovered ? 8 : 0)
                
                content
                    .scaleEffect(scale)
                    .shadow(color: isHovered ? atmosphere.accent.opacity(0.3) : .clear, radius: glowRadius, x: 0, y: 0)
                    .animation(OneDesign.Motion.fast, value: isHovered)
                    .animation(OneDesign.Motion.fast, value: isPressed)
            }
        }
    }
}

extension View {
    public func omlxInteractiveBorder(isFocused: Bool, hasValidation: Bool = false, role: OMLXPageRole = .runtime, isDark: Bool = true) -> some View {
        self.modifier(OneDesign.Interaction.BorderGlowModifier(isFocused: isFocused, hasValidation: hasValidation, role: role, isDark: isDark))
    }
    
    public func omlxButtonInteractiveGlow(isHovered: Bool, isPressed: Bool, role: OMLXPageRole = .runtime, isDark: Bool = true) -> some View {
        self.modifier(OneDesign.Interaction.ButtonInteractiveGlowModifier(isHovered: isHovered, isPressed: isPressed, role: role, isDark: isDark))
    }
}
