import SwiftUI

extension OneDesign {
    public struct SurfaceTokens: Sendable {
        public let window: Color
        public let panel: Color
        public let card: Color
        public let control: Color
        public let overlay: Color
        public let glassTint: Color
        public let border: Color
    }
    
    public enum Surfaces {
        public static let dark = SurfaceTokens(
            window: OneDesign.Colors.spaceBlack,
            panel: OneDesign.Colors.deepCharcoal,
            card: OneDesign.Colors.cardGray,
            control: OneDesign.Colors.inputGray,
            overlay: OneDesign.Colors.elevatedGray,
            glassTint: OneDesign.Colors.deepCharcoal.opacity(0.70),
            border: OneDesign.Colors.borderGray
        )
        
        public static let light = SurfaceTokens(
            window: OneDesign.Colors.stardustWhite,
            panel: OneDesign.Colors.cleanWhite,
            card: OneDesign.Colors.cardLight,
            control: OneDesign.Colors.inputLight,
            overlay: OneDesign.Colors.elevatedLight,
            glassTint: OneDesign.Colors.cleanWhite.opacity(0.70),
            border: OneDesign.Colors.borderLight
        )
    }
}
