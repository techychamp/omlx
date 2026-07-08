import Foundation

protocol DiagnosticsServiceProtocol: Sendable {
    func getCompilerInspection() async throws -> CompilerInspection
    func getExecutionMetrics() async throws -> ExecutionMetrics
    func getAppleMetrics() async throws -> AppleMetrics
    func getBenchmarkReport() async throws -> BenchmarkReport
    func getStats(scope: String, model: String) async throws -> StatsDTO
    @discardableResult func clearStats() async throws -> SimpleStatusResponse
    @discardableResult func clearAlltimeStats() async throws -> SimpleStatusResponse
    @discardableResult func clearSsdCache() async throws -> ClearSsdCacheResponse
    @discardableResult func clearHotCache() async throws -> ClearHotCacheResponse
    func getLogs(lines: Int, file: String?) async throws -> LogsDTO
    
    // Benchmarks
    func startThroughputBench(_ body: BenchStartRequest) async throws -> BenchStartResponse
    func getBenchResults(benchId: String) async throws -> BenchResultsResponse
    func cancelBench(benchId: String) async throws -> BenchCancelResponse
    
    func addAccuracyQueue(_ body: AccuracyQueueAddRequest) async throws -> AccuracyQueueStatus
    func getAccuracyQueueStatus() async throws -> AccuracyQueueStatus
    func removeAccuracyQueue(index: Int) async throws -> AccuracyQueueStatus
    func listAccuracyResults() async throws -> AccuracyResultsResponse
    func resetAccuracyResults() async throws -> SimpleStatusResponse
    func cancelAccuracyBench() async throws -> SimpleStatusResponse
}

actor DiagnosticsService: DiagnosticsServiceProtocol {
    private let client: OMLXClient
    
    init(client: OMLXClient) {
        self.client = client
    }
    
    func getCompilerInspection() async throws -> CompilerInspection {
        return try await client.get("\(RuntimeAPI.v1Diagnostics)/compiler")
    }
    
    func getExecutionMetrics() async throws -> ExecutionMetrics {
        return try await client.get("\(RuntimeAPI.v1Diagnostics)/execution")
    }
    
    func getAppleMetrics() async throws -> AppleMetrics {
        return try await client.get("\(RuntimeAPI.v1Diagnostics)/apple")
    }
    
    func getBenchmarkReport() async throws -> BenchmarkReport {
        return try await client.get(RuntimeAPI.v1Benchmarks)
    }
    
    func getStats(scope: String = "session", model: String = "") async throws -> StatsDTO {
        return try await client.getStats(scope: scope, model: model)
    }
    
    @discardableResult func clearStats() async throws -> SimpleStatusResponse {
        try await client.clearStats()
    }
    
    @discardableResult func clearAlltimeStats() async throws -> SimpleStatusResponse {
        try await client.clearAlltimeStats()
    }
    
    @discardableResult func clearSsdCache() async throws -> ClearSsdCacheResponse {
        return try await client.clearSsdCache()
    }
    
    @discardableResult func clearHotCache() async throws -> ClearHotCacheResponse {
        return try await client.clearHotCache()
    }
    
    func getLogs(lines: Int = 200, file: String? = nil) async throws -> LogsDTO {
        return try await client.getLogs(lines: lines, file: file)
    }
    
    func startThroughputBench(_ body: BenchStartRequest) async throws -> BenchStartResponse {
        return try await client.startThroughputBench(body)
    }
    
    func getBenchResults(benchId: String) async throws -> BenchResultsResponse {
        return try await client.getBenchResults(benchId: benchId)
    }
    
    func cancelBench(benchId: String) async throws -> BenchCancelResponse {
        return try await client.cancelBench(benchId: benchId)
    }
    
    func addAccuracyQueue(_ body: AccuracyQueueAddRequest) async throws -> AccuracyQueueStatus {
        return try await client.addAccuracyQueue(body)
    }
    
    func getAccuracyQueueStatus() async throws -> AccuracyQueueStatus {
        return try await client.getAccuracyQueueStatus()
    }
    
    func removeAccuracyQueue(index: Int) async throws -> AccuracyQueueStatus {
        return try await client.removeAccuracyQueue(index: index)
    }
    
    func listAccuracyResults() async throws -> AccuracyResultsResponse {
        return try await client.listAccuracyResults()
    }
    
    func resetAccuracyResults() async throws -> SimpleStatusResponse {
        return try await client.resetAccuracyResults()
    }
    
    func cancelAccuracyBench() async throws -> SimpleStatusResponse {
        return try await client.cancelAccuracyBench()
    }
}
