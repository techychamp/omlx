import Foundation
@testable import oMLX

actor MockSessionService: SessionServiceProtocol {
    var sessionsToReturn: [SessionInfo] = []
    var sessionToReturn: SessionInfo?
    var errorToThrow: Error?

    func getSessions() async throws -> [SessionInfo] {
        if let error = errorToThrow {
            throw error
        }
        return sessionsToReturn
    }

    func getSession(id: String) async throws -> SessionInfo {
        if let error = errorToThrow {
            throw error
        }
        guard let session = sessionToReturn else {
            fatalError("sessionToReturn not set in mock")
        }
        return session
    }

    func deleteSession(id: String) async throws {
        if let error = errorToThrow {
            throw error
        }
    }
}
