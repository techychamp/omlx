import sys

file_path = "apps/omlx-mac/Sources/Net/DTO/GenerationDTO.swift"
with open(file_path, "r") as f:
    content = f.read()

replacement = """struct ChatMessage: Codable, Sendable, Identifiable {
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
}"""

content = content.replace("""struct ChatMessage: Codable, Sendable {
    let role: String
    let content: String

    init(role: String, content: String) {
        self.role = role
        self.content = content
    }
}""", replacement)

with open(file_path, "w") as f:
    f.write(content)
