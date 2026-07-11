import SwiftUI

// Minimal progress indicator that maps project-specific styles/states
// onto SwiftUI's built-in ProgressView.
enum ProgressIndicatorStyle {
    case linear
    case orbital
}

enum ProgressIndicatorState: Equatable {
    case indeterminate
    case determinate(progress: Double)
}

struct AppProgressIndicator: View {
    let style: ProgressIndicatorStyle
    let state: ProgressIndicatorState

    init(_ style: ProgressIndicatorStyle, state: ProgressIndicatorState) {
        self.style = style
        self.state = state
    }

    var body: some View {
        switch style {
        case .linear:
            switch state {
            case .indeterminate:
                ProgressView()
                    .progressViewStyle(LinearProgressViewStyle())
            case .determinate(let p):
                ProgressView(value: clamp(p))
                    .progressViewStyle(LinearProgressViewStyle())
            }
        case .orbital:
            switch state {
            case .indeterminate:
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle())
            case .determinate(let p):
                ProgressView(value: clamp(p))
                    .progressViewStyle(CircularProgressViewStyle())
            }
        }
    }

    private func clamp(_ value: Double) -> Double {
        guard value.isFinite else { return 0 }
        return min(max(value, 0), 1)
    }
}
