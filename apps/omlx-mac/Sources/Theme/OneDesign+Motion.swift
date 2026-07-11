import SwiftUI

extension OneDesign {
    public enum Motion {
        public static let fast: Animation = .easeOut(duration: 0.15)
        public static let normal: Animation = .easeInOut(duration: 0.25)
        public static let slow: Animation = .easeInOut(duration: 0.4)
        public static let spring: Animation = .spring(response: 0.35, dampingFraction: 0.7)
        
        public static let fastDuration: Double = 0.15
        public static let normalDuration: Double = 0.25
        public static let slowDuration: Double = 0.4
    }
}

// Perpetual Rotation Modifier for Orbital loading animations
public struct OrbitalRotationModifier: ViewModifier {
    @State private var angle: Double = 0.0
    let duration: Double
    
    public func body(content: Content) -> some View {
        content
            .rotationEffect(.degrees(angle))
            .onAppear {
                withAnimation(.linear(duration: duration).repeatForever(autoreverses: false)) {
                    angle = 360.0
                }
            }
    }
}

extension View {
    public func orbitalRotation(duration: Double = 4.0) -> some View {
        self.modifier(OrbitalRotationModifier(duration: duration))
    }
}
