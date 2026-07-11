import SwiftUI

extension OneDesign {
    public enum Shapes {
        // Geometrical components
        public struct ContinuousSquircle: Shape {
            public var cornerRadiusFraction: CGFloat = 0.27
            
            public func path(in rect: CGRect) -> Path {
                let size = min(rect.width, rect.height)
                let radius = size * cornerRadiusFraction
                let roundedRect = RoundedRectangle(cornerRadius: radius, style: .continuous)
                return roundedRect.path(in: rect)
            }
        }
        
        // Clean Circular Arc for progress/loaders
        public struct Arc: Shape {
            public var startAngle: Angle
            public var endAngle: Angle
            public var clockwise: Bool
            
            public func path(in rect: CGRect) -> Path {
                var path = Path()
                let center = CGPoint(x: rect.midX, y: rect.midY)
                let radius = min(rect.width, rect.height) / 2
                path.addArc(center: center, radius: radius, startAngle: startAngle, endAngle: endAngle, clockwise: clockwise)
                return path
            }
        }
    }
}
