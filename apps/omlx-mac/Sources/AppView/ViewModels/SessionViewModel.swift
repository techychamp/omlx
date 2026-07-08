import Foundation
import SwiftUI

@MainActor
@Observable
final class SessionViewModel {
    let service: SessionServiceProtocol

    var sessions: [SessionInfo] = []
    var activeSessionId: String?
    var error: Error?

    init(service: SessionServiceProtocol) {
        self.service = service
    }

    func fetchSessions() async {
        do {
            sessions = try await service.getSessions()
        } catch {
            self.error = error
        }
    }

    func selectSession(_ id: String) {
        activeSessionId = id
    }

    func createNewSession() {
        activeSessionId = nil
    }

    func deleteSession(_ id: String) {
        // TODO: This currently updates local state only.
        // Once the frozen v1 API supports session deletion,
        // this should call `service.deleteSession(id)` asynchronously.
        sessions.removeAll { $0.sessionId == id }
        if activeSessionId == id {
            activeSessionId = nil
        }
    }
}
