import Foundation

protocol ModelManagementServiceProtocol: Sendable {
    func getModels() async throws -> [ModelInfo]
    
    // Admin / Model Management
    func listModels() async throws -> ListModelsResponse
    func loadModel(id: String) async throws -> SimpleStatusResponse
    func unloadModel(id: String) async throws -> SimpleStatusResponse
    func deleteHFModel(modelName: String) async throws -> SimpleStatusResponse
    
    // Settings & Profiles
    func updateModelSettings(id: String, patch: ModelSettingsPatch) async throws -> SimpleStatusResponse
    func listModelProfiles(id: String) async throws -> ProfileListResponse
    func createModelProfile(id: String, body: CreateProfileRequest) async throws -> CreateProfileResponse
    func updateModelProfile(id: String, name: String, body: UpdateProfileRequest) async throws -> UpdateProfileResponse
    func deleteModelProfile(id: String, name: String) async throws -> DeleteResponse
    func applyModelProfile(id: String, name: String) async throws -> ApplyProfileResponse
    func listProfileTemplates() async throws -> TemplateListResponse
    func createProfileTemplate(body: CreateTemplateRequest) async throws -> CreateTemplateResponse
    func updateProfileTemplate(name: String, body: UpdateTemplateRequest) async throws -> UpdateTemplateResponse
    func deleteProfileTemplate(name: String) async throws -> DeleteResponse
    
    // Preset
    func refreshPresetBundle() async throws -> PresetBundleDTO
    
    // HF Downloads
    func listHFTasks() async throws -> HFTaskListResponse
    func startHFDownload(repoId: String, hfToken: String) async throws -> StartHFDownloadResponse
    func cancelHFDownload(taskId: String) async throws -> SimpleStatusResponse
    func retryHFDownload(taskId: String) async throws -> StartHFDownloadResponse
    func removeHFTask(taskId: String) async throws -> SimpleStatusResponse
    func getHFRecommended(mlxOnly: Bool) async throws -> HFRecommendedResponse
    func searchHFModels(query: String, sort: String, limit: Int, mlxOnly: Bool) async throws -> HFSearchResponse
    func getHFModelCard(repoId: String) async throws -> ModelCardDTO
    
    // MS Downloads
    func getMSStatus() async throws -> MSStatusResponse
    func listMSTasks() async throws -> MSTaskListResponse
    func startMSDownload(modelId: String, msToken: String) async throws -> StartMSDownloadResponse
    func cancelMSDownload(taskId: String) async throws -> SimpleStatusResponse
    func retryMSDownload(taskId: String) async throws -> StartMSDownloadResponse
    func removeMSTask(taskId: String) async throws -> SimpleStatusResponse
    func getMSRecommended(mlxOnly: Bool) async throws -> MSRecommendedResponse
    func searchMSModels(query: String, sort: String, limit: Int, mlxOnly: Bool) async throws -> MSSearchResponse
    func getMSModelCard(modelId: String) async throws -> ModelCardDTO
    
    // Quantization
    func listOQModels() async throws -> OQModelsResponse
    func listOQTasks() async throws -> OQTasksResponse
    func estimateOQ(modelPath: String, oqLevel: Double, preserveMtp: Bool) async throws -> OQEstimateResponse
    func startOQQuantization(_ body: OQStartRequest) async throws -> OQStartResponse
    func cancelOQTask(taskId: String) async throws -> SimpleStatusResponse
    func removeOQTask(taskId: String) async throws -> SimpleStatusResponse
    
    // HF Uploads
    func listHFUploadModels() async throws -> HFUploadModelsResponse
    func listHFUploadTasks() async throws -> HFUploadTasksResponse
    func validateHFUploadToken(hfToken: String) async throws -> HFValidateTokenResponse
    func startHFUpload(_ body: HFUploadStartRequest) async throws -> HFUploadStartResponse
    func cancelHFUploadTask(taskId: String) async throws -> SimpleStatusResponse
    func removeHFUploadTask(taskId: String) async throws -> SimpleStatusResponse
}

actor ModelManagementService: ModelManagementServiceProtocol {
    private let client: OMLXClient
    
    init(client: OMLXClient) {
        self.client = client
    }
    
    func getModels() async throws -> [ModelInfo] {
        return try await client.get(RuntimeAPI.v1Models)
    }
    
    // MARK: - Admin / Model Management
    func listModels() async throws -> ListModelsResponse {
        return try await client.listModels()
    }
    func loadModel(id: String) async throws -> SimpleStatusResponse {
        return try await client.loadModel(id: id)
    }
    func unloadModel(id: String) async throws -> SimpleStatusResponse {
        return try await client.unloadModel(id: id)
    }
    func deleteHFModel(modelName: String) async throws -> SimpleStatusResponse {
        return try await client.deleteHFModel(modelName: modelName)
    }
    
    // MARK: - Settings & Profiles
    func updateModelSettings(id: String, patch: ModelSettingsPatch) async throws -> SimpleStatusResponse {
        return try await client.updateModelSettings(id: id, patch: patch)
    }
    func listModelProfiles(id: String) async throws -> ProfileListResponse {
        return try await client.listModelProfiles(id: id)
    }
    func createModelProfile(id: String, body: CreateProfileRequest) async throws -> CreateProfileResponse {
        return try await client.createModelProfile(id: id, body: body)
    }
    func updateModelProfile(id: String, name: String, body: UpdateProfileRequest) async throws -> UpdateProfileResponse {
        return try await client.updateModelProfile(id: id, name: name, body: body)
    }
    func deleteModelProfile(id: String, name: String) async throws -> DeleteResponse {
        return try await client.deleteModelProfile(id: id, name: name)
    }
    func applyModelProfile(id: String, name: String) async throws -> ApplyProfileResponse {
        return try await client.applyModelProfile(id: id, name: name)
    }
    func listProfileTemplates() async throws -> TemplateListResponse {
        return try await client.listProfileTemplates()
    }
    func createProfileTemplate(body: CreateTemplateRequest) async throws -> CreateTemplateResponse {
        return try await client.createProfileTemplate(body: body)
    }
    func updateProfileTemplate(name: String, body: UpdateTemplateRequest) async throws -> UpdateTemplateResponse {
        return try await client.updateProfileTemplate(name: name, body: body)
    }
    func deleteProfileTemplate(name: String) async throws -> DeleteResponse {
        return try await client.deleteProfileTemplate(name: name)
    }
    
    func refreshPresetBundle() async throws -> PresetBundleDTO {
        return try await client.refreshPresetBundle()
    }
    
    // MARK: - HF Downloads
    func listHFTasks() async throws -> HFTaskListResponse {
        return try await client.listHFTasks()
    }
    func startHFDownload(repoId: String, hfToken: String = "") async throws -> StartHFDownloadResponse {
        return try await client.startHFDownload(repoId: repoId, hfToken: hfToken)
    }
    func cancelHFDownload(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.cancelHFDownload(taskId: taskId)
    }
    func retryHFDownload(taskId: String) async throws -> StartHFDownloadResponse {
        return try await client.retryHFDownload(taskId: taskId)
    }
    func removeHFTask(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.removeHFTask(taskId: taskId)
    }
    func getHFRecommended(mlxOnly: Bool = true) async throws -> HFRecommendedResponse {
        return try await client.getHFRecommended(mlxOnly: mlxOnly)
    }
    func searchHFModels(query: String, sort: String = "trending", limit: Int = 20, mlxOnly: Bool = true) async throws -> HFSearchResponse {
        return try await client.searchHFModels(query: query, sort: sort, limit: limit, mlxOnly: mlxOnly)
    }
    func getHFModelCard(repoId: String) async throws -> ModelCardDTO {
        return try await client.getHFModelCard(repoId: repoId)
    }
    
    // MARK: - MS Downloads
    func getMSStatus() async throws -> MSStatusResponse {
        return try await client.getMSStatus()
    }
    func listMSTasks() async throws -> MSTaskListResponse {
        return try await client.listMSTasks()
    }
    func startMSDownload(modelId: String, msToken: String = "") async throws -> StartMSDownloadResponse {
        return try await client.startMSDownload(modelId: modelId, msToken: msToken)
    }
    func cancelMSDownload(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.cancelMSDownload(taskId: taskId)
    }
    func retryMSDownload(taskId: String) async throws -> StartMSDownloadResponse {
        return try await client.retryMSDownload(taskId: taskId)
    }
    func removeMSTask(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.removeMSTask(taskId: taskId)
    }
    func getMSRecommended(mlxOnly: Bool = true) async throws -> MSRecommendedResponse {
        return try await client.getMSRecommended(mlxOnly: mlxOnly)
    }
    func searchMSModels(query: String, sort: String = "trending", limit: Int = 20, mlxOnly: Bool = true) async throws -> MSSearchResponse {
        return try await client.searchMSModels(query: query, sort: sort, limit: limit, mlxOnly: mlxOnly)
    }
    
    func getMSModelCard(modelId: String) async throws -> ModelCardDTO {
        return try await client.getMSModelCard(modelId: modelId)
    }
    
    // MARK: - Quantization
    
    func listOQModels() async throws -> OQModelsResponse {
        return try await client.listOQModels()
    }
    
    func listOQTasks() async throws -> OQTasksResponse {
        return try await client.listOQTasks()
    }
    
    func estimateOQ(modelPath: String, oqLevel: Double, preserveMtp: Bool) async throws -> OQEstimateResponse {
        return try await client.estimateOQ(modelPath: modelPath, oqLevel: oqLevel, preserveMtp: preserveMtp)
    }
    
    func startOQQuantization(_ body: OQStartRequest) async throws -> OQStartResponse {
        return try await client.startOQQuantization(body)
    }
    
    func cancelOQTask(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.cancelOQTask(taskId: taskId)
    }
    
    func removeOQTask(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.removeOQTask(taskId: taskId)
    }
    
    // MARK: - HF Uploads
    
    func listHFUploadModels() async throws -> HFUploadModelsResponse {
        return try await client.listHFUploadModels()
    }
    
    func listHFUploadTasks() async throws -> HFUploadTasksResponse {
        return try await client.listHFUploadTasks()
    }
    
    func validateHFUploadToken(hfToken: String) async throws -> HFValidateTokenResponse {
        return try await client.validateHFUploadToken(hfToken: hfToken)
    }
    
    func startHFUpload(_ body: HFUploadStartRequest) async throws -> HFUploadStartResponse {
        return try await client.startHFUpload(body)
    }
    
    func cancelHFUploadTask(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.cancelHFUploadTask(taskId: taskId)
    }
    
    func removeHFUploadTask(taskId: String) async throws -> SimpleStatusResponse {
        return try await client.removeHFUploadTask(taskId: taskId)
    }
}

struct ModelInfo: Decodable, Sendable {
    let apiVersion: String?
    let id: String
    let ready: Bool
}
