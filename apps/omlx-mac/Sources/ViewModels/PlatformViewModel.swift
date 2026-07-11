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
    var warningMessage: String? = nil
    
    init(service: PlatformServiceProtocol, sessionService: SessionServiceProtocol) {
        self.service = service
        self.sessionService = sessionService
    }
    
    func loadData() async {
        isLoading = true
        errorMessage = nil
        warningMessage = nil
        
        async let fetchStatus = service.getStatus()
        async let fetchCapabilities = service.getCapabilities()
        async let fetchServerInfo = service.getServerInfo()
        
        do {
            status = try await fetchStatus
            capabilities = try await fetchCapabilities
            serverInfo = try await fetchServerInfo
        } catch {
            errorMessage = error.omlxDescription
            isLoading = false
            return
        }

        do {
            sessions = try await sessionService.getSessions()
        } catch {
            sessions = []
            warningMessage = "Sessions unavailable: \(error.omlxDescription)"
        }
        
        isLoading = false
    }
}
