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

enum DeveloperTraceStatus: String, Sendable {
    case pending = "Pending"
    case running = "Running"
    case completed = "Completed"
    case failed = "Failed"
}

struct DeveloperTraceStep: Identifiable, Sendable {
    let id: String
    let name: String
    let icon: String
    var status: DeveloperTraceStatus
    var detail: String?
}

struct DeveloperEndpointEvent: Identifiable, Sendable {
    let id = UUID()
    let method: String
    let path: String
    var status: DeveloperTraceStatus
    var durationMs: Int?
    var detail: String
}

@MainActor
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
    var endpointEvents: [DeveloperEndpointEvent] = []
    var traceSteps: [DeveloperTraceStep] = DeveloperToolsViewModel.defaultTraceSteps()
    var responseSummaries: [String] = []

    var error: String?
    var isLoading = false

    init(services: AppServices) {
        self.platformService = services.platformService
        self.diagnosticsService = services.diagnosticsService
        self.generationService = services.generationService
        self.sessionService = services.sessionService
    }

    func refreshData() async {
        isLoading = true
        defer { isLoading = false }
        error = nil
        endpointEvents = []
        responseSummaries = []
        traceSteps = Self.defaultTraceSteps()
        updateTrace("View", .completed, detail: "Developer Studio visible")
        updateTrace("ViewModel", .running, detail: "Refreshing diagnostics")

        await fetch(
            method: "GET",
            path: RuntimeAPI.v1Runtime,
            stage: "Runtime",
            assign: { self.runtimeStatus = $0 },
            summarize: { "Runtime \($0.status), uptime \(Int($0.uptime))s, version \($0.version)" },
            call: { try await self.platformService.getStatus() }
        )
        await fetch(
            method: "GET",
            path: "\(RuntimeAPI.v1Runtime)/info",
            stage: "Runtime",
            assign: { self.serverInfo = $0 },
            summarize: { "Server \($0.host):\($0.port), backend \($0.backend)" },
            call: { try await self.platformService.getServerInfo() }
        )
        await fetch(
            method: "GET",
            path: "\(RuntimeAPI.v1Runtime)/capabilities",
            stage: "Runtime",
            assign: { self.capabilities = $0 },
            summarize: {
                "Capabilities MoE=\($0.supportsMoe), speculation=\($0.supportsSpeculation), diffusion=\($0.supportsDiffusion)"
            },
            call: { try await self.platformService.getCapabilities() }
        )
        await fetch(
            method: "GET",
            path: "\(RuntimeAPI.v1Diagnostics)/compiler",
            stage: "Compiler",
            assign: { self.compilerInspection = $0 },
            summarize: { "Compiler \($0.compilerVersion), graph \($0.graphStatus)" },
            call: { try await self.diagnosticsService.getCompilerInspection() }
        )
        await fetch(
            method: "GET",
            path: "\(RuntimeAPI.v1Diagnostics)/execution",
            stage: "Execution",
            assign: { self.executionMetrics = $0 },
            summarize: { "Execution tokens prompt=\($0.promptTokens), completion=\($0.completionTokens), total=\($0.totalTokens)" },
            call: { try await self.diagnosticsService.getExecutionMetrics() }
        )
        await fetch(
            method: "GET",
            path: "\(RuntimeAPI.v1Diagnostics)/apple",
            stage: "Execution",
            assign: { self.appleMetrics = $0 },
            summarize: { "Apple memory=\($0.memoryUsed) bytes, GPU=\($0.gpuUtilization)%, ANE=\($0.aneUtilization)%" },
            call: { try await self.diagnosticsService.getAppleMetrics() }
        )
        await fetch(
            method: "GET",
            path: RuntimeAPI.v1Benchmarks,
            stage: "Execution",
            assign: { self.benchmarkReport = $0 },
            summarize: { "Benchmark throughput=\($0.throughput), generation TPS=\($0.tokensPerSecond)" },
            call: { try await self.diagnosticsService.getBenchmarkReport() }
        )
        await fetch(
            method: "GET",
            path: RuntimeAPI.v1Sessions,
            stage: "Runtime",
            assign: { self.sessions = $0 },
            summarize: { "Sessions \($0.count)" },
            call: { try await self.sessionService.getSessions() }
        )

        updateTrace("Service", endpointEvents.contains { $0.status == .failed } ? .failed : .completed,
                    detail: "\(endpointEvents.count) endpoint calls")
        updateTrace("OMLXClient", endpointEvents.contains { $0.status == .failed } ? .failed : .completed,
                    detail: "HTTP client completed refresh")
        updateTrace("Response", responseSummaries.isEmpty ? .pending : .completed,
                    detail: responseSummaries.isEmpty ? "No decoded responses" : "\(responseSummaries.count) decoded responses")
        updateTrace("ViewModel", endpointEvents.contains { $0.status == .failed } ? .failed : .completed,
                    detail: endpointEvents.contains { $0.status == .failed } ? "Refresh completed with failures" : "Refresh completed")

        let failures = endpointEvents.filter { $0.status == .failed }
        if !failures.isEmpty {
            error = failures.map { "\($0.path): \($0.detail)" }.joined(separator: "\n")
        }
    }

    private func fetch<T>(
        method: String,
        path: String,
        stage: String,
        assign: (T) -> Void,
        summarize: (T) -> String,
        call: () async throws -> T
    ) async {
        updateTrace("Service", .running, detail: path)
        updateTrace("OMLXClient", .running, detail: "\(method) \(path)")
        updateTrace(stage, .running, detail: path)
        let startedAt = Date()
        let index = endpointEvents.count
        endpointEvents.append(DeveloperEndpointEvent(
            method: method,
            path: path,
            status: .running,
            durationMs: nil,
            detail: "Request started"
        ))

        do {
            let value = try await call()
            assign(value)
            let durationMs = Int(Date().timeIntervalSince(startedAt) * 1000)
            let summary = summarize(value)
            endpointEvents[index].status = .completed
            endpointEvents[index].durationMs = durationMs
            endpointEvents[index].detail = summary
            responseSummaries.append(summary)
            updateTrace(stage, .completed, detail: summary)
        } catch {
            let durationMs = Int(Date().timeIntervalSince(startedAt) * 1000)
            endpointEvents[index].status = .failed
            endpointEvents[index].durationMs = durationMs
            endpointEvents[index].detail = error.omlxDescription
            updateTrace(stage, .failed, detail: error.omlxDescription)
        }
    }

    private func updateTrace(_ name: String, _ status: DeveloperTraceStatus, detail: String? = nil) {
        guard let index = traceSteps.firstIndex(where: { $0.name == name }) else { return }
        traceSteps[index].status = status
        traceSteps[index].detail = detail
    }

    private static func defaultTraceSteps() -> [DeveloperTraceStep] {
        [
            DeveloperTraceStep(id: "view", name: "View", icon: "macwindow", status: .pending, detail: nil),
            DeveloperTraceStep(id: "viewmodel", name: "ViewModel", icon: "brain", status: .pending, detail: nil),
            DeveloperTraceStep(id: "service", name: "Service", icon: "network", status: .pending, detail: nil),
            DeveloperTraceStep(id: "client", name: "OMLXClient", icon: "globe", status: .pending, detail: nil),
            DeveloperTraceStep(id: "runtime", name: "Runtime", icon: "cpu", status: .pending, detail: nil),
            DeveloperTraceStep(id: "compiler", name: "Compiler", icon: "gearshape.2", status: .pending, detail: nil),
            DeveloperTraceStep(id: "execution", name: "Execution", icon: "bolt.fill", status: .pending, detail: nil),
            DeveloperTraceStep(id: "response", name: "Response", icon: "arrow.uturn.left", status: .pending, detail: nil),
        ]
    }

    func clearHistory() {
        endpointEvents = []
        responseSummaries = []
        traceSteps = Self.defaultTraceSteps()
        error = nil
    }
}
