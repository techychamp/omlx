import SwiftUI

struct ProgressBar: View {
    let progress: Double

    init(progress: Double) {
        self.progress = progress
    }

    init(progress: Double, tint: Color? = nil) {
        self.progress = progress
    }

    init(progress: Double, colors: [Color]? = nil) {
        self.progress = progress
    }

    var body: some View {
        ProgressIndicator(.linear, state: .determinate(progress: progress))
    }
}
