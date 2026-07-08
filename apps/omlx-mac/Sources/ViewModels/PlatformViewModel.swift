import Foundation
import SwiftUI

@MainActor
@Observable
final class PlatformViewModel {
    private let service: PlatformServiceProtocol
    private let sessionService: SessionServiceProtocol
    
    var status: RuntimeStatus?
    var capabilities: CapabilityReport?
    var serverInfo: ServerInfo?
    var sessions: [SessionInfo] = []
    
    var isLoading: Bool = false
    var errorMessage: String? = nil
    
    init(service: PlatformServiceProtocol, sessionService: SessionServiceProtocol) {
        self.service = service
        self.sessionService = sessionService
    }
    
    func loadData() async {
        isLoading = true
        errorMessage = nil
        
        async let fetchStatus = service.getStatus()
        async let fetchCapabilities = service.getCapabilities()
        async let fetchServerInfo = service.getServerInfo()
        async let fetchSessions = sessionService.getSessions()
        
        do {
            status = try await fetchStatus
            capabilities = try await fetchCapabilities
            serverInfo = try await fetchServerInfo
            sessions = try await fetchSessions
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}
