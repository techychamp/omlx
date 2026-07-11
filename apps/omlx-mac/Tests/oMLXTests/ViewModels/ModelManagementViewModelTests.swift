import XCTest
@testable import oMLX

@MainActor
final class ModelManagementViewModelTests: XCTestCase {
    
    func testLoadModelsSuccess() async {
        let mockService = MockModelManagementService()
        await mockService.setModelsToReturn([
            ModelInfo(apiVersion: "v1", id: "llama-3-8b", ready: true),
            ModelInfo(apiVersion: "v1", id: "mistral-7b", ready: true)
        ])
        
        let viewModel = ModelManagementViewModel(service: mockService)
        XCTAssertTrue(viewModel.models.isEmpty)
        
        await viewModel.loadModels()
        
        XCTAssertEqual(viewModel.models.count, 2)
        XCTAssertNil(viewModel.errorMessage)
        XCTAssertFalse(viewModel.isLoading)
    }
    
    func testLoadModelsFailure() async {
        let mockService = MockModelManagementService()
        await mockService.setErrorToThrow(NSError(domain: "Test", code: -1, userInfo: [NSLocalizedDescriptionKey: "Network Error"]))
        
        let viewModel = ModelManagementViewModel(service: mockService)
        
        await viewModel.loadModels()
        
        XCTAssertTrue(viewModel.models.isEmpty)
        XCTAssertEqual(viewModel.errorMessage, "Network Error")
        XCTAssertFalse(viewModel.isLoading)
    }
    
    func testSearchFiltering() async {
        let mockService = MockModelManagementService()
        await mockService.setModelsToReturn([
            ModelInfo(apiVersion: "v1", id: "Apple-Model", ready: true),
            ModelInfo(apiVersion: "v1", id: "Banana-Model", ready: true),
            ModelInfo(apiVersion: "v1", id: "apricot-model", ready: false)
        ])
        
        let viewModel = ModelManagementViewModel(service: mockService)
        await viewModel.loadModels()
        
        viewModel.searchQuery = "ap"
        let filtered = viewModel.filteredAndSortedModels
        XCTAssertEqual(filtered.count, 2)
        XCTAssertTrue(filtered.contains { $0.id == "Apple-Model" })
        XCTAssertTrue(filtered.contains { $0.id == "apricot-model" })
    }
    
    func testSorting() async {
        let mockService = MockModelManagementService()
        await mockService.setModelsToReturn([
            ModelInfo(apiVersion: "v1", id: "Zebra", ready: true),
            ModelInfo(apiVersion: "v1", id: "Apple", ready: true),
            ModelInfo(apiVersion: "v1", id: "Mango", ready: false)
        ])
        
        let viewModel = ModelManagementViewModel(service: mockService)
        await viewModel.loadModels()
        
        viewModel.sortOrder = .nameAscending
        let ascending = viewModel.filteredAndSortedModels
        XCTAssertEqual(ascending.map { $0.id }, ["Apple", "Mango", "Zebra"])
        
        viewModel.sortOrder = .nameDescending
        let descending = viewModel.filteredAndSortedModels
        XCTAssertEqual(descending.map { $0.id }, ["Zebra", "Mango", "Apple"])
    }
}

// Helpers for the actor mock
extension MockModelManagementService {
    func setModelsToReturn(_ models: [ModelInfo]) {
        self.modelsToReturn = models
    }
    func setErrorToThrow(_ error: Error?) {
        self.errorToThrow = error
    }
}
