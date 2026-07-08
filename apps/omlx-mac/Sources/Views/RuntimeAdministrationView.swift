import SwiftUI

struct RuntimeAdministrationView: View {
    let services: AppServices
    
    @State private var viewModel: PlatformViewModel
    @Environment(\.omlxTheme) private var theme
    
    init(services: AppServices) {
        self.services = services
        self._viewModel = State(initialValue: PlatformViewModel(service: services.platformService, sessionService: services.sessionService))
    }
    
    var body: some View {
        VStack(spacing: 24) {
            if viewModel.isLoading {
                ProgressView()
                    .accessibilityLabel("Loading runtime administration data")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else if let error = viewModel.errorMessage {
                VStack(spacing: 12) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundStyle(.red)
                    Text(error)
                        .font(.omlxText(14))
                        .foregroundStyle(theme.text)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Error loading runtime administration data: \(error)")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    VStack(alignment: .leading, spacing: 20) {
                        RuntimeOverviewCard(status: viewModel.status, serverInfo: viewModel.serverInfo, capabilities: viewModel.capabilities)
                        RuntimeConfigurationCard(serverInfo: viewModel.serverInfo)
                        SessionManagementView(sessions: viewModel.sessions)
                        
                        Divider()
                        
                        HStack(spacing: 16) {
                            Button("Open Diagnostics") {
                                services.requestedSection = .diagnostics
                            }
                            .buttonStyle(.omlx(.normal))
                            .accessibilityLabel("Open Diagnostics workspace")
                            
                            Button("Compiler Explorer") {
                                // Assuming compiler explorer exists under diagnostics or developer
                                services.requestedSection = .developer
                            }
                            .buttonStyle(.omlx(.normal))
                            .accessibilityLabel("Open Developer Studio")
                        }
                        .padding(.top, 8)
                    }
                    .padding()
                }
            }
        }
        .task {
            await viewModel.loadData()
        }
    }
}

private struct RuntimeOverviewCard: View {
    let status: RuntimeStatus?
    let serverInfo: ServerInfo?
    let capabilities: CapabilityReport?
    
    @Environment(\.omlxTheme) private var theme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Runtime Overview")
                .font(.omlxText(16, weight: .semibold))
                .foregroundStyle(theme.text)
                .accessibilityAddTraits(.isHeader)
            
            VStack(alignment: .leading, spacing: 8) {
                InfoRow(label: "Status", value: status?.status ?? "Unknown")
                InfoRow(label: "Version", value: status?.version ?? "Unknown")
                InfoRow(label: "Uptime", value: status != nil ? String(format: "%.1fs", status!.uptime) : "Unknown")
                InfoRow(label: "Backend", value: serverInfo?.backend ?? "Unknown")
                
                if let caps = capabilities {
                    let capStrings = [
                        caps.supportsMoe ? "MoE" : nil,
                        caps.supportsSpeculation ? "Speculation" : nil,
                        caps.supportsDiffusion ? "Diffusion" : nil
                    ].compactMap { $0 }.joined(separator: ", ")
                    InfoRow(label: "Capabilities", value: capStrings.isEmpty ? "Basic" : capStrings)
                }
            }
        }
        .padding()
        .background(theme.groupBg)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(theme.groupBorder, lineWidth: 1)
        )
    }
}

private struct RuntimeConfigurationCard: View {
    let serverInfo: ServerInfo?
    
    @Environment(\.omlxTheme) private var theme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Runtime Configuration")
                .font(.omlxText(16, weight: .semibold))
                .foregroundStyle(theme.text)
                .accessibilityAddTraits(.isHeader)
            
            VStack(alignment: .leading, spacing: 8) {
                InfoRow(label: "Host", value: serverInfo?.host ?? "Unknown")
                InfoRow(label: "Port", value: serverInfo != nil ? "\(serverInfo!.port)" : "Unknown")
                InfoRow(label: "API Version", value: serverInfo?.apiVersion ?? "v1")
            }
        }
        .padding()
        .background(theme.groupBg)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(theme.groupBorder, lineWidth: 1)
        )
    }
}

private struct InfoRow: View {
    let label: String
    let value: String
    
    @Environment(\.omlxTheme) private var theme
    
    var body: some View {
        HStack {
            Text(label)
                .font(.omlxText(13, weight: .medium))
                .foregroundStyle(theme.textSecondary)
                .frame(width: 120, alignment: .leading)
            Text(value)
                .font(.omlxText(13))
                .foregroundStyle(theme.text)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(label): \(value)")
    }
}
