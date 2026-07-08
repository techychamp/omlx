import Foundation
@testable import oMLX

actor MockModelManagementService: ModelManagementServiceProtocol {
    var modelsToReturn: [ModelInfo] = []
    var errorToThrow: Error?

    func getModels() async throws -> [ModelInfo] {
        if let error = errorToThrow {
            throw error
        }
        return modelsToReturn
    }
}
