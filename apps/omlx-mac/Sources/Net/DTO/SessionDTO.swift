import Foundation

struct SessionInfo: Decodable, Sendable {
    let apiVersion: String?
    let sessionId: String
    let createdAt: Date
}

struct SessionState: Decodable, Sendable {
    let apiVersion: String?
    let sessionId: String
    let isActive: Bool
}
