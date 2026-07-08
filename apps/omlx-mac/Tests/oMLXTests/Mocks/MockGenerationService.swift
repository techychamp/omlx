import Foundation
@testable import oMLX

actor MockGenerationService: GenerationServiceProtocol {
    var generateResult: Result<GenerateResponse, Error>?
    var streamResult: Result<[GenerationChunk], Error>?
    
    init() {}
    
    func setGenerateResult(_ result: Result<GenerateResponse, Error>) {
        self.generateResult = result
    }
    
    func setStreamResult(_ result: Result<[GenerationChunk], Error>) {
        self.streamResult = result
    }
    
    func generate(request: GenerateRequest) async throws -> GenerateResponse {
        if let result = generateResult {
            return try result.get()
        }
        throw NSError(domain: "MockError", code: 0, userInfo: [NSLocalizedDescriptionKey: "No mock result set"])
    }
    
    nonisolated func stream(request: GenerateRequest) async throws -> AsyncThrowingStream<GenerationChunk, Error> {
        return AsyncThrowingStream { continuation in
            Task {
                let result = await self.streamResult
                if let result = result {
                    switch result {
                    case .success(let chunks):
                        for chunk in chunks {
                            continuation.yield(chunk)
                        }
                        continuation.finish()
                    case .failure(let error):
                        continuation.finish(throwing: error)
                    }
                } else {
                    continuation.finish(throwing: NSError(domain: "MockError", code: 0, userInfo: [NSLocalizedDescriptionKey: "No mock stream result set"]))
                }
            }
        }
    }
}
