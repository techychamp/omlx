import Foundation
@testable import oMLX

actor MockPlatformService: PlatformServiceProtocol {
    var statusToReturn: RuntimeStatus?
    var capabilitiesToReturn: CapabilityReport?
    var serverInfoToReturn: ServerInfo?
    var errorToThrow: Error?

    func getStatus() async throws -> RuntimeStatus {
        if let error = errorToThrow {
            throw error
        }
        guard let status = statusToReturn else {
            fatalError("statusToReturn not set in mock")
        }
        return status
    }

    func getCapabilities() async throws -> CapabilityReport {
        if let error = errorToThrow {
            throw error
        }
        guard let caps = capabilitiesToReturn else {
            fatalError("capabilitiesToReturn not set in mock")
        }
        return caps
    }

    func getServerInfo() async throws -> ServerInfo {
        if let error = errorToThrow {
            throw error
        }
        guard let info = serverInfoToReturn else {
            fatalError("serverInfoToReturn not set in mock")
        }
        return info
    }
}
