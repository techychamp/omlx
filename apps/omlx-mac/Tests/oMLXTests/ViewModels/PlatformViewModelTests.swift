import XCTest
@testable import oMLX

@MainActor
final class PlatformViewModelTests: XCTestCase {
    
    func testLoadDataSuccess() async {
        let mockPlatform = MockPlatformService()
        await mockPlatform.setStatus(RuntimeStatus(apiVersion: "v1", status: "Running", uptime: 100, version: "1.0.0"))
        await mockPlatform.setCapabilities(CapabilityReport(apiVersion: "v1", supportsMoe: true, supportsSpeculation: false, supportsDiffusion: true))
        await mockPlatform.setServerInfo(ServerInfo(apiVersion: "v1", host: "localhost", port: 8080, backend: "MLX"))
        
        let mockSession = MockSessionService()
        await mockSession.setSessions([SessionInfo(apiVersion: "v1", sessionId: "123", createdAt: Date())])
        
        let viewModel = PlatformViewModel(service: mockPlatform, sessionService: mockSession)
        
        await viewModel.loadData()
        
        XCTAssertNil(viewModel.errorMessage)
        XCTAssertEqual(viewModel.status?.status, "Running")
        XCTAssertEqual(viewModel.capabilities?.supportsMoe, true)
        XCTAssertEqual(viewModel.serverInfo?.port, 8080)
        XCTAssertEqual(viewModel.sessions.count, 1)
        XCTAssertFalse(viewModel.isLoading)
    }
    
    func testLoadDataFailure() async {
        let mockPlatform = MockPlatformService()
        await mockPlatform.setErrorToThrow(NSError(domain: "Test", code: -1, userInfo: [NSLocalizedDescriptionKey: "Platform Error"]))
        
        let mockSession = MockSessionService()
        
        let viewModel = PlatformViewModel(service: mockPlatform, sessionService: mockSession)
        
        await viewModel.loadData()
        
        XCTAssertEqual(viewModel.errorMessage, "Platform Error")
        XCTAssertNil(viewModel.status)
        XCTAssertFalse(viewModel.isLoading)
    }
}

// Helpers
extension MockPlatformService {
    func setStatus(_ status: RuntimeStatus) { self.statusToReturn = status }
    func setCapabilities(_ caps: CapabilityReport) { self.capabilitiesToReturn = caps }
    func setServerInfo(_ info: ServerInfo) { self.serverInfoToReturn = info }
    func setErrorToThrow(_ error: Error?) { self.errorToThrow = error }
}

extension MockSessionService {
    func setSessions(_ sessions: [SessionInfo]) { self.sessionsToReturn = sessions }
}
