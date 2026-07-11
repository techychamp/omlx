import SwiftUI

public struct ProgressIndicator: View {
    public enum Kind {
        case linear
        case circular
        case orbital
    }
    
    public enum State {
        case determinate(progress: Double)
        case indeterminate
    }
    
    let kind: Kind
    let state: State
    let role: OMLXPageRole?
    
    @Environment(\.omlxTheme) private var theme
    @Environment(\.omlxPageRole) private var defaultRole
    
    public init(_ kind: Kind = .linear, state: State = .indeterminate, role: OMLXPageRole? = nil) {
        self.kind = kind
        self.state = state
        self.role = role
    }
    
    private var activeRole: OMLXPageRole {
        role ?? defaultRole
    }
    
    private var activeAccent: Color {
        OneDesign.SemanticRoles.resolveAtmosphere(for: activeRole, isDark: theme.isDark).accent
    }
    
    private var glowColor: Color {
        OneDesign.SemanticRoles.resolveAtmosphere(for: activeRole, isDark: theme.isDark).glowColor
    }
    
    public var body: some View {
        switch kind {
        case .linear:
            linearView
        case .circular:
            circularView
        case .orbital:
            orbitalView
        }
    }
    
    // MARK: - Linear Progress
    private var linearView: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule()
                    .fill(theme.codeBg)
                
                Capsule()
                    .fill(activeAccent)
                    .frame(width: geo.size.width * CGFloat(determinateProgress))
                    .shadow(color: glowColor, radius: 2)
                    .animation(OneDesign.Motion.normal, value: determinateProgress)
            }
        }
        .frame(height: 4)
    }
    
    // MARK: - Circular Progress
    private var circularView: some View {
        ZStack {
            Circle()
                .stroke(theme.codeBg, lineWidth: 2.5)
            
            if isIndeterminate {
                OneDesign.Shapes.Arc(startAngle: .degrees(0), endAngle: .degrees(90), clockwise: false)
                    .stroke(activeAccent, style: StrokeStyle(lineWidth: 2.5, lineCap: .round))
                    .orbitalRotation(duration: 1.0)
            } else {
                OneDesign.Shapes.Arc(startAngle: .degrees(-90), endAngle: .degrees(-90 + 360 * determinateProgress), clockwise: false)
                    .stroke(activeAccent, style: StrokeStyle(lineWidth: 2.5, lineCap: .round))
                    .animation(OneDesign.Motion.normal, value: determinateProgress)
            }
        }
        .frame(width: 24, height: 24)
    }
    
    // MARK: - Orbital Progress (Cosmic Geometry)
    private var orbitalView: some View {
        ZStack {
            // Faint lattice grid or background orbit path
            Circle()
                .stroke(theme.codeBg.opacity(0.4), lineWidth: 1)
                .frame(width: 48, height: 48)
            
            // Central Nucleus
            Circle()
                .fill(activeAccent)
                .frame(width: 10, height: 10)
                .shadow(color: glowColor, radius: 6)
            
            // Orbiting Planet
            Circle()
                .fill(activeAccent.opacity(0.8))
                .frame(width: 6, height: 6)
                .offset(x: 24) // radius of the orbit (48 / 2)
                .orbitalRotation(duration: activeRole == .execution ? 2.5 : 4.0) // faster for execution role
        }
        .frame(width: 60, height: 60)
    }
    
    // Helpers
    private var determinateProgress: Double {
        switch state {
        case .determinate(let progress):
            return max(0.0, min(progress, 1.0))
        case .indeterminate:
            return 0.0
        }
    }
    
    private var isIndeterminate: Bool {
        switch state {
        case .determinate: return false
        case .indeterminate: return true
        }
    }
}
