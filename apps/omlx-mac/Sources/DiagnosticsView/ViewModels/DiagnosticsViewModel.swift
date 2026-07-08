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

    init(diagnosticsService: DiagnosticsServiceProtocol) {
        self.diagnosticsService = diagnosticsService
    }

    func fetchAll() async {
        isLoading = true
        error = nil
        do {
            async let fetchCompiler = diagnosticsService.getCompilerInspection()
            async let fetchExecution = diagnosticsService.getExecutionMetrics()
            async let fetchApple = diagnosticsService.getAppleMetrics()
            async let fetchBenchmark = diagnosticsService.getBenchmarkReport()

            self.compilerInspection = try await fetchCompiler
            self.executionMetrics = try await fetchExecution
            self.appleMetrics = try await fetchApple
            self.benchmarkReport = try await fetchBenchmark
        } catch {
            self.error = error
        }
        isLoading = false
    }
}
