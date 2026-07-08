import Foundation

struct GenerateRequest: Encodable, Sendable {
    var apiVersion: String = "v1"
    let model: String
    let messages: [ChatMessage]
    let stream: Bool
    
    init(model: String, messages: [ChatMessage], stream: Bool = false) {
        self.model = model
        self.messages = messages
        self.stream = stream
    }
}

struct ChatMessage: Codable, Sendable, Identifiable {
    var id: UUID = UUID()
    let role: String
    let content: String
    
    enum CodingKeys: String, CodingKey {
        case role
        case content
    }

    init(role: String, content: String) {
        self.role = role
        self.content = content
    }
}

struct GenerateResponse: Decodable, Sendable {
    let apiVersion: String?
    let id: String
    let choices: [Choice]
}

struct Choice: Decodable, Sendable {
    let message: ChatMessage
    let finishReason: String?
}

struct GenerationChunk: Decodable, Sendable {
    let apiVersion: String?
    let id: String
    let choices: [ChunkChoice]
}

struct ChunkChoice: Decodable, Sendable {
    let delta: MessageDelta
    let finishReason: String?
}

struct MessageDelta: Decodable, Sendable {
    let role: String?
    let content: String?
}
