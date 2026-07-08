import Foundation
import SwiftUI
import Combine

enum DeveloperStudioTab: String, CaseIterable, Identifiable, Sendable {
    case apiExplorer = "API Explorer"
    case requestInspector = "Request Inspector"
    case responseInspector = "Response Inspector"
    case runtimeEvents = "Runtime Events"
    case logExplorer = "Log Explorer"
    case traceViewer = "Trace Viewer"

    var id: String { rawValue }
}

@Observable
final class DeveloperToolsViewModel: @unchecked Sendable {
    var selectedTab: DeveloperStudioTab = .apiExplorer

    // Services
    private let platformService: PlatformServiceProtocol
    private let diagnosticsService: DiagnosticsServiceProtocol
    private let generationService: GenerationServiceProtocol
    private let sessionService: SessionServiceProtocol

    // State
    var runtimeStatus: RuntimeStatus?
    var serverInfo: ServerInfo?
    var capabilities: CapabilityReport?
    var compilerInspection: CompilerInspection?
    var executionMetrics: ExecutionMetrics?
    var appleMetrics: AppleMetrics?
    var benchmarkReport: BenchmarkReport?
    var sessions: [SessionInfo] = []

    var error: String?
    var isLoading = false

    init(services: AppServices) {
        self.platformService = services.platform
        self.diagnosticsService = services.diagnostics
        self.generationService = services.generation
        self.sessionService = services.sessionService
    }

    func refreshData() async {
        isLoading = true
        defer { isLoading = false }
        error = nil

        do {
            async let fetchStatus = platformService.getStatus()
            async let fetchInfo = platformService.getServerInfo()
            async let fetchCaps = platformService.getCapabilities()
            async let fetchCompiler = diagnosticsService.getCompilerInspection()
            async let fetchExec = diagnosticsService.getExecutionMetrics()
            async let fetchApple = diagnosticsService.getAppleMetrics()
            async let fetchBench = diagnosticsService.getBenchmarkReport()
            async let fetchSessions = sessionService.getSessions()

            let (status, info, caps, compiler, exec, apple, bench, sessionList) = try await (
                fetchStatus, fetchInfo, fetchCaps, fetchCompiler, fetchExec, fetchApple, fetchBench, fetchSessions
            )

            await MainActor.run {
                self.runtimeStatus = status
                self.serverInfo = info
                self.capabilities = caps
                self.compilerInspection = compiler
                self.executionMetrics = exec
                self.appleMetrics = apple
                self.benchmarkReport = bench
                self.sessions = sessionList
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
            }
        }
    }

    func clearHistory() {
        // Clear local history logic here
    }
}
