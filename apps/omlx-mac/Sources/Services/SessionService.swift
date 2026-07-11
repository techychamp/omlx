import Foundation

protocol SessionServiceProtocol: Sendable {
    func getSessions() async throws -> [SessionInfo]
    func getSession(id: String) async throws -> SessionInfo
    func deleteSession(id: String) async throws
}

actor SessionService: SessionServiceProtocol {
    private let client: OMLXClient
    
    init(client: OMLXClient) {
        self.client = client
    }
    
    func getSessions() async throws -> [SessionInfo] {
        return try await client.get(RuntimeAPI.v1Sessions)
    }
    
    func getSession(id: String) async throws -> SessionInfo {
        return try await client.get("\(RuntimeAPI.v1Sessions)/\(id)")
    }
    
    func deleteSession(id: String) async throws {
        let _: SimpleStatusResponse = try await client.delete("\(RuntimeAPI.v1Sessions)/\(id)")
    }
}
