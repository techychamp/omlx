import sys

file_path = "apps/omlx-mac/Sources/AppView/Screens/Workspace/RuntimeStatusView.swift"
with open(file_path, "r") as f:
    content = f.read()

# Remove timer state
content = content.replace("    @State private var timer: Timer?\n    ", "")

# Update onAppear to just fetchStatus
on_appear_replacement = """        .onAppear {
            Task { await fetchStatus() }
        }"""
content = content.replace("""        .onAppear {
            startPolling()
        }""", on_appear_replacement)

# Remove onDisappear
content = content.replace("""        .onDisappear {
            stopPolling()
        }""", "")

# Remove polling methods
content = content.replace("""    private func startPolling() {
        Task { await fetchStatus() }
        timer = Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
            Task { @MainActor in
                await fetchStatus()
            }
        }
    }

    private func stopPolling() {
        timer?.invalidate()
        timer = nil
    }""", "")

with open(file_path, "w") as f:
    f.write(content)
