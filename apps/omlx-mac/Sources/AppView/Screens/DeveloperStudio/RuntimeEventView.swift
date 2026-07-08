import SwiftUI

struct RuntimeEventView: View {
    let viewModel: DeveloperToolsViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.error {
                    Text("Error: \(error)")
                        .foregroundColor(.red)
                } else {
                    if let status = viewModel.runtimeStatus {
                        SectionHeader(title: "Runtime Status")
                        VStack(alignment: .leading) {
                            Text("Status: \(status.status)")
                            Text("Version: \(status.version)")
                            Text("Uptime: \(status.uptime)s")
                        }
                        .padding()
                        .background(theme.groupBg)
                        .cornerRadius(8)
                    }

                    if let caps = viewModel.capabilities {
                        SectionHeader(title: "Capabilities")
                        VStack(alignment: .leading) {
                            Text("MoE: \(caps.supportsMoe ? "Yes" : "No")")
                            Text("Speculation: \(caps.supportsSpeculation ? "Yes" : "No")")
                            Text("Diffusion: \(caps.supportsDiffusion ? "Yes" : "No")")
                        }
                        .padding()
                        .background(theme.groupBg)
                        .cornerRadius(8)
                    }

                    if !viewModel.sessions.isEmpty {
                        SectionHeader(title: "Sessions")
                        ForEach(viewModel.sessions, id: \.id) { session in
                            VStack(alignment: .leading) {
                                Text("ID: \(session.id)")
                                Text("Title: \(session.title)")
                            }
                            .padding()
                            .background(theme.groupBg)
                            .cornerRadius(8)
                        }
                    }
                }
            }
            .padding()
        }
        .task {
            await viewModel.refreshData()
        }
    }
}
