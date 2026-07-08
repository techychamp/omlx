import Foundation

struct CompilerInspection: Decodable, Sendable {
    let apiVersion: String?
    let compilerVersion: String
    let graphStatus: String
}

struct ExecutionMetrics: Decodable, Sendable {
    let apiVersion: String?
    let promptTokens: Int
    let completionTokens: Int
    let totalTokens: Int
}

struct AppleMetrics: Decodable, Sendable {
    let apiVersion: String?
    let memoryUsed: Int64
    let aneUtilization: Double
    let gpuUtilization: Double
}

struct BenchmarkReport: Decodable, Sendable {
    let apiVersion: String?
    let throughput: Double
    let tokensPerSecond: Double
}
