import Foundation

protocol PlatformServiceProtocol: Sendable {
    func getStatus() async throws -> RuntimeStatus
    func getCapabilities() async throws -> CapabilityReport
    func getServerInfo() async throws -> ServerInfo
    func getGlobalSettings() async throws -> GlobalSettingsDTO
    func updateGlobalSettings(_ patch: GlobalSettingsPatch) async throws -> UpdateGlobalSettingsResponse
    
    // Auth Management
    func setupApiKey(_ key: String, confirm: String) async throws -> SimpleStatusResponse
    func createSubKey(key: String, name: String) async throws -> CreateSubKeyResponse
    func deleteSubKey(key: String) async throws -> SimpleStatusResponse
    func updateClientAuth(apiKey: String?) async
    func getDeviceInfo() async throws -> DeviceInfoDTO
}

actor PlatformService: PlatformServiceProtocol {
    private let client: OMLXClient
    
    init(client: OMLXClient) {
        self.client = client
    }
    
    func getStatus() async throws -> RuntimeStatus {
        return try await client.get(RuntimeAPI.v1Runtime)
    }
    
    func getCapabilities() async throws -> CapabilityReport {
        return try await client.get("\(RuntimeAPI.v1Runtime)/capabilities")
    }
    
    func getServerInfo() async throws -> ServerInfo {
        return try await client.get("\(RuntimeAPI.v1Runtime)/info")
    }
    
    func getGlobalSettings() async throws -> GlobalSettingsDTO {
        return try await client.getGlobalSettings()
    }
    
    func updateGlobalSettings(_ patch: GlobalSettingsPatch) async throws -> UpdateGlobalSettingsResponse {
        return try await client.updateGlobalSettings(patch)
    }
    
    // MARK: - Auth Management
    
    func setupApiKey(_ key: String, confirm: String) async throws -> SimpleStatusResponse {
        return try await client.setupApiKey(key, confirm: confirm)
    }
    
    func createSubKey(key: String, name: String) async throws -> CreateSubKeyResponse {
        return try await client.createSubKey(key: key, name: name)
    }
    
    func deleteSubKey(key: String) async throws -> SimpleStatusResponse {
        return try await client.deleteSubKey(key: key)
    }
    
    func updateClientAuth(apiKey: String?) async {
        await MainActor.run {
            client.configure(host: client.host, port: client.port, apiKey: apiKey)
        }
    }
    
    func getDeviceInfo() async throws -> DeviceInfoDTO {
        return try await client.getDeviceInfo()
    }
}
