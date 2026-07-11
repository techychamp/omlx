import Foundation
import SwiftUI

@MainActor
@Observable
final class ModelManagementViewModel {
    private let service: ModelManagementServiceProtocol
    
    var models: [ModelInfo] = []
    var isLoading: Bool = false
    var errorMessage: String? = nil
    
    var searchQuery: String = ""
    var sortOrder: SortOrder = .nameAscending
    
    enum SortOrder: String, CaseIterable, Identifiable {
        case nameAscending = "Name (A-Z)"
        case nameDescending = "Name (Z-A)"
        
        var id: String { rawValue }
    }
    
    init(service: ModelManagementServiceProtocol) {
        self.service = service
    }
    
    func loadModels() async {
        isLoading = true
        errorMessage = nil
        do {
            models = try await service.getModels()
        } catch {
            errorMessage = error.omlxDescription
        }
        isLoading = false
    }
    
    var filteredAndSortedModels: [ModelInfo] {
        var result = models
        
        if !searchQuery.isEmpty {
            // Case-insensitive and diacritic-insensitive search
            let options: String.CompareOptions = [.caseInsensitive, .diacriticInsensitive]
            result = result.filter { $0.id.range(of: searchQuery, options: options) != nil }
        }
        
        // Stable sorting
        result.sort { (a, b) -> Bool in
            switch sortOrder {
            case .nameAscending:
                return a.id.localizedStandardCompare(b.id) == .orderedAscending
            case .nameDescending:
                return a.id.localizedStandardCompare(b.id) == .orderedDescending
            }
        }
        
        return result
    }
}
