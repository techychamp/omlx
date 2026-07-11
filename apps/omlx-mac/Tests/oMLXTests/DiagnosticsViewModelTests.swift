import XCTest
import Combine
@testable import oMLX

@MainActor
final class DiagnosticsViewModelTests: XCTestCase {

    class MockDiagnosticsService: DiagnosticsServiceProtocol {
        var compilerInspectionResult: Result<CompilerInspection, Error> = .success(CompilerInspection(apiVersion: "v1", compilerVersion: "1.0", graphStatus: "Optimized"))
        var executionMetricsResult: Result<ExecutionMetrics, Error> = .success(ExecutionMetrics(apiVersion: "v1", promptTokens: 10, completionTokens: 20, totalTokens: 30))
        var appleMetricsResult: Result<AppleMetrics, Error> = .success(AppleMetrics(apiVersion: "v1", memoryUsed: 1024, aneUtilization: 0.5, gpuUtilization: 0.8))
        var benchmarkReportResult: Result<BenchmarkReport, Error> = .success(BenchmarkReport(apiVersion: "v1", throughput: 100.0, tokensPerSecond: 50.0))

        func getCompilerInspection() async throws -> CompilerInspection {
            return try compilerInspectionResult.get()
        }
        func getExecutionMetrics() async throws -> ExecutionMetrics {
            return try executionMetricsResult.get()
        }
        func getAppleMetrics() async throws -> AppleMetrics {
            return try appleMetricsResult.get()
        }
        func getBenchmarkReport() async throws -> BenchmarkReport {
            return try benchmarkReportResult.get()
        }
    }

    func testFetchAllSuccess() async throws {
        let mockService = MockDiagnosticsService()
        let viewModel = DiagnosticsViewModel(diagnosticsService: mockService)

        await viewModel.fetchAll()

        XCTAssertNotNil(viewModel.compilerInspection)
        XCTAssertNotNil(viewModel.executionMetrics)
        XCTAssertNotNil(viewModel.appleMetrics)
        XCTAssertNotNil(viewModel.benchmarkReport)
        XCTAssertNil(viewModel.error)
    }

    func testFetchAllFailure() async throws {
        let mockService = MockDiagnosticsService()
        mockService.compilerInspectionResult = .failure(NSError(domain: "test", code: -1, userInfo: nil))

        let viewModel = DiagnosticsViewModel(diagnosticsService: mockService)
        await viewModel.fetchAll()

        XCTAssertNotNil(viewModel.error)
    }
}
