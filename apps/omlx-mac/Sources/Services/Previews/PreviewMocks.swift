import Foundation

actor PreviewGenerationService: GenerationServiceProtocol {
    init() {}
    
    func generate(request: GenerateRequest) async throws -> GenerateResponse {
        return GenerateResponse(
            apiVersion: "v1",
            id: "chatcmpl-preview",
            choices: [Choice(message: ChatMessage(role: "assistant", content: "This is a preview response."), finishReason: "stop")]
        )
    }
    
    nonisolated func stream(request: GenerateRequest) async throws -> AsyncThrowingStream<GenerationChunk, Error> {
        return AsyncThrowingStream { continuation in
            continuation.yield(GenerationChunk(
                apiVersion: "v1",
                id: "chatcmpl-preview",
                choices: [ChunkChoice(delta: MessageDelta(role: "assistant", content: "This "), finishReason: nil)]
            ))
            continuation.yield(GenerationChunk(
                apiVersion: "v1",
                id: "chatcmpl-preview",
                choices: [ChunkChoice(delta: MessageDelta(role: nil, content: "is a "), finishReason: nil)]
            ))
            continuation.yield(GenerationChunk(
                apiVersion: "v1",
                id: "chatcmpl-preview",
                choices: [ChunkChoice(delta: MessageDelta(role: nil, content: "preview."), finishReason: "stop")]
            ))
            continuation.finish()
        }
    }
}

actor PreviewPlatformService: PlatformServiceProtocol {
    init() {}
    
    func getStatus() async throws -> RuntimeStatus {
        return RuntimeStatus(apiVersion: "v1", status: "ok", uptime: 3600, version: "0.1.0-preview")
    }
    
    func getCapabilities() async throws -> CapabilityReport {
        return CapabilityReport(apiVersion: "v1", supportsMoe: true, supportsSpeculation: true, supportsDiffusion: false)
    }
    
    func getServerInfo() async throws -> ServerInfo {
        return ServerInfo(apiVersion: "v1", host: "127.0.0.1", port: 8000, backend: "mlx")
    }
    
    func getGlobalSettings() async throws -> GlobalSettingsDTO {
        let json = "{}"
        return try JSONDecoder().decode(GlobalSettingsDTO.self, from: json.data(using: .utf8)!)
    }
    
    func updateGlobalSettings(_ patch: GlobalSettingsPatch) async throws -> UpdateGlobalSettingsResponse {
        return UpdateGlobalSettingsResponse(success: true, message: nil, runtimeApplied: nil)
    }
    
    func setupApiKey(_ key: String, confirm: String) async throws -> SimpleStatusResponse {
        return SimpleStatusResponse(status: "ok", message: nil, success: true)
    }
    
    func createSubKey(key: String, name: String) async throws -> CreateSubKeyResponse {
        return CreateSubKeyResponse(success: true, subKey: nil)
    }
    
    func deleteSubKey(key: String) async throws -> SimpleStatusResponse {
        return SimpleStatusResponse(status: "ok", message: nil, success: true)
    }
    
    func updateClientAuth(apiKey: String?) async {}
    
    func getDeviceInfo() async throws -> DeviceInfoDTO {
        return parseMock("{}")
    }
}

actor PreviewDiagnosticsService: DiagnosticsServiceProtocol {
    init() {}
    
    func getCompilerInspection() async throws -> CompilerInspection { return parseMock("{}") }
    func getExecutionMetrics() async throws -> ExecutionMetrics { return parseMock("{}") }
    func getAppleMetrics() async throws -> AppleMetrics { return parseMock("{}") }
    func getBenchmarkReport() async throws -> BenchmarkReport { return parseMock("{}") }
    func getStats(scope: String, model: String) async throws -> StatsDTO { return parseMock("{\"totalTokensServed\":0,\"totalCachedTokens\":0,\"cacheEfficiency\":0.0,\"totalPromptTokens\":0,\"totalCompletionTokens\":0,\"totalRequests\":0,\"avgPrefillTps\":0.0,\"avgGenerationTps\":0.0,\"uptimeSeconds\":0.0,\"activeModels\":{\"models\":[]}}") }
    func clearStats() async throws -> SimpleStatusResponse { return SimpleStatusResponse(status: "ok", message: nil, success: true) }
    func clearAlltimeStats() async throws -> SimpleStatusResponse { return SimpleStatusResponse(status: "ok", message: nil, success: true) }
    func clearSsdCache() async throws -> ClearSsdCacheResponse { return parseMock("{}") }
    func clearHotCache() async throws -> ClearHotCacheResponse { return parseMock("{}") }
    func getLogs(lines: Int, file: String?) async throws -> LogsDTO { return LogsDTO(logs: "", totalLines: 0, logFile: "", availableFiles: []) }
    
    // Benchmarks
    func startThroughputBench(_ body: BenchStartRequest) async throws -> BenchStartResponse { return BenchStartResponse(benchId: "bench1", status: "started", totalTests: 1) }
    func getBenchResults(benchId: String) async throws -> BenchResultsResponse { return BenchResultsResponse(benchId: "bench1", status: "completed", results: [], error: nil, uploadState: nil) }
    func cancelBench(benchId: String) async throws -> BenchCancelResponse { return BenchCancelResponse(status: "cancelled", benchId: "bench1") }
    
    func addAccuracyQueue(_ body: AccuracyQueueAddRequest) async throws -> AccuracyQueueStatus { return AccuracyQueueStatus(running: false, currentModel: "", currentBenchId: "", lastProgress: nil, phase: nil, queue: []) }
    func getAccuracyQueueStatus() async throws -> AccuracyQueueStatus { return AccuracyQueueStatus(running: false, currentModel: "", currentBenchId: "", lastProgress: nil, phase: nil, queue: []) }
    func removeAccuracyQueue(index: Int) async throws -> AccuracyQueueStatus { return AccuracyQueueStatus(running: false, currentModel: "", currentBenchId: "", lastProgress: nil, phase: nil, queue: []) }
    func listAccuracyResults() async throws -> AccuracyResultsResponse { return AccuracyResultsResponse(results: [], running: false, currentModel: "", currentBenchId: "") }
    func resetAccuracyResults() async throws -> SimpleStatusResponse { return SimpleStatusResponse(status: "ok", message: nil, success: true) }
    func cancelAccuracyBench() async throws -> SimpleStatusResponse { return SimpleStatusResponse(status: "ok", message: nil, success: true) }
}

private func parseMock<T: Decodable>(_ json: String) -> T {
    return try! JSONDecoder().decode(T.self, from: json.data(using: .utf8)!)
}
