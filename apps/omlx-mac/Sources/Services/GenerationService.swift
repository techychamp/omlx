import Foundation

protocol GenerationServiceProtocol: Sendable {
    func generate(request: GenerateRequest) async throws -> GenerateResponse
    func stream(request: GenerateRequest) async throws -> AsyncThrowingStream<GenerationChunk, Error>
}

actor GenerationService: GenerationServiceProtocol {
    private let client: OMLXClient
    
    init(client: OMLXClient) {
        self.client = client
    }
    
    func generate(request: GenerateRequest) async throws -> GenerateResponse {
        return try await client.post(RuntimeAPI.v1ChatCompletions, body: request)
    }
    
    nonisolated func stream(request: GenerateRequest) async throws -> AsyncThrowingStream<GenerationChunk, Error> {
        do {
            let encoder = JSONEncoder()
            let body = try encoder.encode(request)
            return await client.stream(method: "POST", path: RuntimeAPI.v1ChatCompletions, body: body)
        } catch {
            return AsyncThrowingStream { continuation in
                continuation.finish(throwing: error)
            }
        }
    }
}
