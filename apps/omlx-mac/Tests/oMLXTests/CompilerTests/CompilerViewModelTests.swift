import XCTest
@testable import oMLX

final class MockDiagnosticsService: DiagnosticsServiceProtocol {
    func getCompilerInspection() async throws -> CompilerInspection {
        return CompilerInspection(apiVersion: "v1", compilerVersion: "1.0.0-mock", graphStatus: "compiled")
    }

    func getExecutionMetrics() async throws -> ExecutionMetrics {
        return ExecutionMetrics(apiVersion: "v1", promptTokens: 10, completionTokens: 20, totalTokens: 30)
    }

    func getAppleMetrics() async throws -> AppleMetrics {
        return AppleMetrics(apiVersion: "v1", memoryUsed: 1024, aneUtilization: 0.5, gpuUtilization: 0.8)
    }

    func getBenchmarkReport() async throws -> BenchmarkReport {
        return BenchmarkReport(apiVersion: "v1", throughput: 50.0, tokensPerSecond: 100.0)
    }
}

@MainActor
final class CompilerViewModelTests: XCTestCase {
    func testLoadFetchesCompilerInspection() async {
        let mockService = MockDiagnosticsService()
        let viewModel = CompilerViewModel(diagnosticsService: mockService)

        XCTAssertNil(viewModel.compilerInspection)
        XCTAssertFalse(viewModel.isLoading)

        await viewModel.load()

        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
        XCTAssertNotNil(viewModel.compilerInspection)
        XCTAssertEqual(viewModel.compilerInspection?.compilerVersion, "1.0.0-mock")
        XCTAssertEqual(viewModel.compilerInspection?.graphStatus, "compiled")
    }
}
