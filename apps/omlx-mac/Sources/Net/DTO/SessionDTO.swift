import Foundation

struct SessionInfo: Decodable, Sendable {
    let apiVersion: String?
    let sessionId: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case apiVersion
        case sessionId
        case createdAt
    }

    init(apiVersion: String?, sessionId: String, createdAt: Date) {
        self.apiVersion = apiVersion
        self.sessionId = sessionId
        self.createdAt = createdAt
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        apiVersion = try container.decodeIfPresent(String.self, forKey: .apiVersion)
        sessionId = try container.decode(String.self, forKey: .sessionId)
        createdAt = try Self.decodeDate(from: container, forKey: .createdAt)
    }

    private static func decodeDate(
        from container: KeyedDecodingContainer<CodingKeys>,
        forKey key: CodingKeys
    ) throws -> Date {
        if let seconds = try? container.decode(Double.self, forKey: key) {
            return Date(timeIntervalSince1970: seconds)
        }
        if let string = try? container.decode(String.self, forKey: key) {
            if let seconds = Double(string) {
                return Date(timeIntervalSince1970: seconds)
            }
            let iso = ISO8601DateFormatter()
            if let date = iso.date(from: string) {
                return date
            }
        }
        return Date.distantPast
    }
}

struct SessionState: Decodable, Sendable {
    let apiVersion: String?
    let sessionId: String
    let isActive: Bool
}
