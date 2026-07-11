import SwiftUI

extension OneDesign {
    public enum Typography {
        public static func omlxDisplay(_ weight: Font.Weight = .semibold) -> Font {
            .system(size: 24, weight: weight)
        }
        
        public static func omlxTitle(_ weight: Font.Weight = .semibold) -> Font {
            .system(size: 18, weight: weight)
        }
        
        public static func omlxHeading(_ weight: Font.Weight = .semibold) -> Font {
            .system(size: 14, weight: weight)
        }
        
        public static func omlxBody(_ weight: Font.Weight = .medium) -> Font {
            .system(size: 13, weight: weight)
        }
        
        public static func omlxCaption(_ weight: Font.Weight = .regular) -> Font {
            .system(size: 11, weight: weight)
        }
        
        public static func omlxCode(_ weight: Font.Weight = .regular) -> Font {
            .system(size: 13, weight: weight, design: .monospaced)
        }
    }
}
