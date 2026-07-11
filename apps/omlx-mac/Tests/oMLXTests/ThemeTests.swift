import AppKit
import SwiftUI
import XCTest
@testable import oMLX

final class ThemeTests: XCTestCase {

    func testLightWindowBackgroundUsesStardustWhite() {
        let actual = resolvedRGBA(OMLXTheme.light.windowBg, appearance: .aqua)
        
        // #F3F4F6 is roughly R: 0.953, G: 0.957, B: 0.965
        XCTAssertEqual(actual.red, 0.953, accuracy: 0.01)
        XCTAssertEqual(actual.green, 0.957, accuracy: 0.01)
        XCTAssertEqual(actual.blue, 0.965, accuracy: 0.01)
    }

    func testDarkWindowBackgroundUsesSpaceBlack() {
        let actual = resolvedRGBA(OMLXTheme.dark.windowBg, appearance: .darkAqua)
        
        // #0B0C10 is roughly R: 0.043, G: 0.047, B: 0.063
        XCTAssertEqual(actual.red, 0.043, accuracy: 0.01)
        XCTAssertEqual(actual.green, 0.047, accuracy: 0.01)
        XCTAssertEqual(actual.blue, 0.063, accuracy: 0.01)
    }

    func testLightGroupBackgroundIsCardLight() {
        let actual = resolvedRGBA(OMLXTheme.light.groupBg, appearance: .aqua)
        
        // #E5E7EB is roughly R: 0.898, G: 0.906, B: 0.922
        XCTAssertEqual(actual.red, 0.898, accuracy: 0.01)
        XCTAssertEqual(actual.green, 0.906, accuracy: 0.01)
        XCTAssertEqual(actual.blue, 0.922, accuracy: 0.01)
    }

    private typealias RGBA = (
        red: CGFloat,
        green: CGFloat,
        blue: CGFloat,
        alpha: CGFloat
    )

    private func resolvedRGBA(_ color: Color, appearance: NSAppearance.Name) -> RGBA {
        let nsColor = NSColor(color)
        var components: RGBA?
        NSAppearance(named: appearance)!.performAsCurrentDrawingAppearance {
            let resolved = nsColor.usingColorSpace(.sRGB)!
            components = (
                red: resolved.redComponent,
                green: resolved.greenComponent,
                blue: resolved.blueComponent,
                alpha: resolved.alphaComponent
            )
        }
        return components!
    }
}
