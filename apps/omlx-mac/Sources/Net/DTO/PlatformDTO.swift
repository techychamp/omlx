import Foundation

struct RuntimeStatus: Decodable, Sendable {
    let apiVersion: String?
    let status: String
    let uptime: TimeInterval
    let version: String
}

struct CapabilityReport: Decodable, Sendable {
    let apiVersion: String?
    let supportsMoe: Bool
    let supportsSpeculation: Bool
    let supportsDiffusion: Bool
}

struct ServerInfo: Decodable, Sendable {
    let apiVersion: String?
    let host: String
    let port: Int
    let backend: String
}
