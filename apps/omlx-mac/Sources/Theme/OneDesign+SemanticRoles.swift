import SwiftUI

public enum OMLXPageRole: String, Sendable, CaseIterable {
    case execution
    case runtime
    case planning
    case observation
    case analytics
}

extension OneDesign {
    public struct Atmosphere: Sendable {
        public let accent: Color
        public let glowColor: Color
        public let defaultAnimation: Animation
        public let hasGridOverlay: Bool
        public let progressStyle: ProgressIndicatorStyle
        
        public enum ProgressIndicatorStyle: Sendable {
            case orbital
            case circular
            case linear
        }
    }
    
    public enum SemanticRoles {
        public static func resolveAtmosphere(for role: OMLXPageRole, isDark: Bool) -> Atmosphere {
            switch role {
            case .execution:
                return Atmosphere(
                    accent: isDark ? OneDesign.Colors.goldDark : OneDesign.Colors.goldLight,
                    glowColor: (isDark ? OneDesign.Colors.goldDark : OneDesign.Colors.goldLight).opacity(0.25),
                    defaultAnimation: OneDesign.Motion.fast, // Faster motion for active execution
                    hasGridOverlay: false,
                    progressStyle: .orbital
                )
            case .runtime:
                return Atmosphere(
                    accent: isDark ? OneDesign.Colors.blueDark : OneDesign.Colors.blueLight,
                    glowColor: (isDark ? OneDesign.Colors.blueDark : OneDesign.Colors.blueLight).opacity(0.20),
                    defaultAnimation: OneDesign.Motion.normal,
                    hasGridOverlay: false,
                    progressStyle: .circular
                )
            case .planning:
                return Atmosphere(
                    accent: isDark ? OneDesign.Colors.violetDark : OneDesign.Colors.violetLight,
                    glowColor: (isDark ? OneDesign.Colors.violetDark : OneDesign.Colors.violetLight).opacity(0.30),
                    defaultAnimation: OneDesign.Motion.slow, // Deliberate/structured pacing for compiler/planning
                    hasGridOverlay: true, // Show faint network grid overlay for plans
                    progressStyle: .linear
                )
            case .observation:
                return Atmosphere(
                    accent: isDark ? OneDesign.Colors.cyanDark : OneDesign.Colors.cyanLight,
                    glowColor: (isDark ? OneDesign.Colors.cyanDark : OneDesign.Colors.cyanLight).opacity(0.18),
                    defaultAnimation: OneDesign.Motion.normal,
                    hasGridOverlay: true, // Grid lattices for timelines
                    progressStyle: .linear
                )
            case .analytics:
                return Atmosphere(
                    accent: isDark ? OneDesign.Colors.emeraldDark : OneDesign.Colors.emeraldLight,
                    glowColor: (isDark ? OneDesign.Colors.emeraldDark : OneDesign.Colors.emeraldLight).opacity(0.22),
                    defaultAnimation: OneDesign.Motion.normal,
                    hasGridOverlay: false,
                    progressStyle: .circular
                )
            }
        }
    }
}
