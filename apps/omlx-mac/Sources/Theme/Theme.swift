// Design tokens for the macOS settings UI.
//
// Surface, text, selection, and control colors intentionally resolve through
// dynamic AppKit system colors so the app tracks System Settings across light
// mode, dark mode, accent colors, accessibility contrast, and future macOS
// appearance updates.

import SwiftUI

// MARK: - Token table

struct OMLXTheme: Sendable {
    let isDark: Bool

    // Surfaces
    let windowBg: Color
    let sidebarBg: Color
    let sidebarBorder: Color
    let contentBg: Color
    let toolbarBg: Color
    let toolbarBorder: Color
    let groupBg: Color
    let groupBorder: Color
    let rowSep: Color
    let separator: Color

    // Text
    let text: Color
    let textSecondary: Color
    let textTertiary: Color

    // Accent + selection
    let accent: Color
    let accentSoft: Color
    let accentText: Color
    let selBg: Color
    let hoverBg: Color

    // Controls + inputs
    let controlBg: Color
    let controlBgHover: Color
    let glassBg: Color
    let glassBgStrong: Color
    let inputBg: Color
    let inputBorder: Color
    let inputBorderFocus: Color

    // Status
    let greenDot: Color
    let amberDot: Color
    let redDot: Color
    let blueDot: Color

    // Code + status backgrounds
    let codeBg: Color
    let warningBg: Color
    let warningText: Color
    let successBg: Color
    let successText: Color

    // Desktop wash gradient stops (radial background composed in PR 6's shell).
    let desktopWashTopLeft: Color
    let desktopWashBottomRight: Color
    let desktopWashBase: Color

    // Metrics
    let cornerRadius: CGFloat = 14
    let rowRadius: CGFloat = 10
    let groupHighlightTopOpacity: Double
    let groupShadowOpacity: Double
}

extension OMLXTheme {
    static let light = OMLXTheme.cosmicLight
    static let dark = OMLXTheme.cosmicDark
}

// MARK: - Environment

private struct OMLXThemeKey: EnvironmentKey {
    static let defaultValue: OMLXTheme = .light
}

private struct OMLXPageRoleKey: EnvironmentKey {
    static let defaultValue: OMLXPageRole = .runtime
}

extension EnvironmentValues {
    var omlxTheme: OMLXTheme {
        get { self[OMLXThemeKey.self] }
        set { self[OMLXThemeKey.self] = newValue }
    }
    
    public var omlxPageRole: OMLXPageRole {
        get { self[OMLXPageRoleKey.self] }
        set { self[OMLXPageRoleKey.self] = newValue }
    }
}

private struct OMLXThemeBinder: ViewModifier {
    @Environment(\.colorScheme) private var scheme
    func body(content: Content) -> some View {
        content.environment(\.omlxTheme, scheme == .dark ? .dark : .light)
    }
}

extension View {
    /// Resolves `\.omlxTheme` from the current `\.colorScheme`. Apply once at
    /// the AppView shell (PR 6) so every descendant primitive reads the right
    /// palette without explicit prop-drilling.
    func omlxThemed() -> some View { modifier(OMLXThemeBinder()) }
    
    public func omlxPageRole(_ role: OMLXPageRole) -> some View {
        self.environment(\.omlxPageRole, role)
    }
}

// MARK: - Color helpers

extension Color {
    /// Solid black with the given opacity. Mirrors JSX `rgba(0,0,0,X)`.
    static func black(_ alpha: Double) -> Color {
        Color(.sRGB, white: 0, opacity: alpha)
    }

    /// Solid white with the given opacity. Mirrors JSX `rgba(255,255,255,X)`.
    static func white(_ alpha: Double) -> Color {
        Color(.sRGB, white: 1, opacity: alpha)
    }

    /// Construct from packed 24-bit RGB hex, e.g. `Color(rgb24: 0x007AFF)`.
    init(rgb24: UInt32, opacity: Double = 1.0) {
        let r = Double((rgb24 >> 16) & 0xFF) / 255
        let g = Double((rgb24 >> 8) & 0xFF) / 255
        let b = Double(rgb24 & 0xFF) / 255
        self.init(.sRGB, red: r, green: g, blue: b, opacity: opacity)
    }
}

// MARK: - Typography conveniences

extension Font {
    /// SF Pro Text-y body. macOS picks the right SF variant automatically by size.
    static func omlxText(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight)
    }
    /// Display weight for headlines (size auto-promotes on macOS at ≥ 20pt).
    static func omlxDisplay(_ size: CGFloat, weight: Font.Weight = .semibold) -> Font {
        .system(size: size, weight: weight)
    }
    /// Monospaced (SF Mono fallback chain).
    static func omlxMono(_ size: CGFloat, weight: Font.Weight = .regular) -> Font {
        .system(size: size, weight: weight, design: .monospaced)
    }
}
