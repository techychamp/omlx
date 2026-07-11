import Foundation
import Combine

@MainActor
final class DiagnosticsViewModel: ObservableObject {
    private let diagnosticsService: DiagnosticsServiceProtocol

    @Published var compilerInspection: CompilerInspection?
    @Published var executionMetrics: ExecutionMetrics?
    @Published var appleMetrics: AppleMetrics?
    @Published var benchmarkReport: BenchmarkReport?

    @Published var isLoading = false
    @Published var error: Error?
    @Published var sectionErrors: [DiagnosticsSection: Error] = [:]

    init(diagnosticsService: DiagnosticsServiceProtocol) {
        self.diagnosticsService = diagnosticsService
    }

    func fetchAll() async {
        isLoading = true
        error = nil
        sectionErrors = [:]

        await fetchCompilerInspection()
        await fetchExecutionMetrics()
        await fetchAppleMetrics()
        await fetchBenchmarkReport()

        error = sectionErrors.values.first
        isLoading = false
    }

    func error(for section: DiagnosticsSection) -> Error? {
        sectionErrors[section]
    }

    private func fetchCompilerInspection() async {
        do {
            compilerInspection = try await diagnosticsService.getCompilerInspection()
        } catch {
            sectionErrors[.explorer] = error
        }
    }

    private func fetchExecutionMetrics() async {
        do {
            executionMetrics = try await diagnosticsService.getExecutionMetrics()
        } catch {
            sectionErrors[.runtime] = error
        }
    }

    private func fetchAppleMetrics() async {
        do {
            appleMetrics = try await diagnosticsService.getAppleMetrics()
        } catch {
            sectionErrors[.apple] = error
            sectionErrors[.resources] = error
        }
    }

    private func fetchBenchmarkReport() async {
        do {
            benchmarkReport = try await diagnosticsService.getBenchmarkReport()
        } catch {
            sectionErrors[.benchmarks] = error
        }
    }
}

enum DiagnosticsSection: String, CaseIterable, Hashable, Identifiable {
    case runtime
    case apple
    case benchmarks
    case execution
    case resources
    case explorer

    var id: String { rawValue }

    var title: String {
        switch self {
        case .runtime: return "Runtime Metrics"
        case .apple: return "Apple Silicon"
        case .benchmarks: return "Benchmark Center"
        case .execution: return "Execution Timeline"
        case .resources: return "Resource Dashboard"
        case .explorer: return "Diagnostics Explorer"
        }
    }

    var systemImage: String {
        switch self {
        case .runtime: return "timer"
        case .apple: return "cpu"
        case .benchmarks: return "chart.bar"
        case .execution: return "clock"
        case .resources: return "memorychip"
        case .explorer: return "magnifyingglass"
        }
    }
}
