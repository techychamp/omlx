import SwiftUI

extension OneDesign {
    public struct IconToken: Sendable {
        public let size: CGFloat
        public let weight: Font.Weight
        public let strokeWidth: CGFloat
    }
    
    public enum Icons {
        public static let primary = IconToken(size: 24, weight: .semibold, strokeWidth: 1.5)
        public static let secondary = IconToken(size: 18, weight: .medium, strokeWidth: 1.2)
        public static let status = IconToken(size: 12, weight: .medium, strokeWidth: 1.2)
        public static let navigation = IconToken(size: 16, weight: .medium, strokeWidth: 1.2)
        public static let execution = IconToken(size: 20, weight: .semibold, strokeWidth: 1.5)
    }
}
