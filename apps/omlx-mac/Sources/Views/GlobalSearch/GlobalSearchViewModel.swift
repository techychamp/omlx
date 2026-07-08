import SwiftUI
import Combine

enum GlobalSearchResultType: String {
    case navigation = "Navigation"
    case model = "Model"
    case session = "Session"
    case diagnostic = "Diagnostic"
    case compiler = "Compiler"
}

struct GlobalSearchResult: Identifiable, Hashable {
    let id = UUID()
    let title: String
    let subtitle: String?
    let type: GlobalSearchResultType
    let targetSection: AppSection
}

@MainActor
final class GlobalSearchViewModel: ObservableObject {
    @Published var query: String = ""
    @Published var results: [GlobalSearchResult] = []
    @Published var isSearching: Bool = false
    
    private let services: AppServices
    private var searchTask: Task<Void, Never>?
    
    init(services: AppServices) {
        self.services = services
    }
    
    func performSearch() {
        searchTask?.cancel()
        
        let trimmedQuery = query.trimmingCharacters(in: .whitespacesAndNewlines)
        
        if trimmedQuery.isEmpty {
            results = defaultNavigationResults()
            isSearching = false
            return
        }
        
        isSearching = true
        
        searchTask = Task {
            var aggregated: [GlobalSearchResult] = []
            
            // 1. Navigation
            let navResults = defaultNavigationResults().filter {
                $0.title.localizedCaseInsensitiveContains(trimmedQuery)
            }
            aggregated.append(contentsOf: navResults)
            
            // 2. Models
            if let models = try? await services.modelManagementService.getModels() {
                let matchedModels = models.filter { $0.id.localizedCaseInsensitiveContains(trimmedQuery) }
                aggregated.append(contentsOf: matchedModels.map {
                    GlobalSearchResult(title: $0.id, subtitle: "Ready: \($0.ready)", type: .model, targetSection: .modelManagement)
                })
            }
            
            // 3. Sessions
            if let sessions = try? await services.sessionService.getSessions() {
                let matchedSessions = sessions.filter { $0.sessionId.localizedCaseInsensitiveContains(trimmedQuery) }
                aggregated.append(contentsOf: matchedSessions.map {
                    GlobalSearchResult(title: $0.sessionId, subtitle: "Created: \($0.createdAt)", type: .session, targetSection: .runtimeAdministration)
                })
            }
            
            // 4. Diagnostics / Compiler (mock logic based on what services actually provide in their DTOs)
            // The API freeze means we can only use available DTO data. DiagnosticsService has runtime events.
            // If we have actual endpoints for compiler reports, we'd search them here. For now we just route.
            
            if !Task.isCancelled {
                self.results = aggregated
                self.isSearching = false
            }
        }
    }
    
    private func defaultNavigationResults() -> [GlobalSearchResult] {
        return [
            GlobalSearchResult(title: "Status", subtitle: "System Status & Overview", type: .navigation, targetSection: .status),
            GlobalSearchResult(title: "Models", subtitle: "Model Management", type: .navigation, targetSection: .modelManagement),
            GlobalSearchResult(title: "Runtime Administration", subtitle: "Runtime Config & Sessions", type: .navigation, targetSection: .runtimeAdministration),
            GlobalSearchResult(title: "Diagnostics", subtitle: "Performance & Health", type: .navigation, targetSection: .diagnostics),
            GlobalSearchResult(title: "Developer Studio", subtitle: "API & Trace Explorer", type: .navigation, targetSection: .developer)
        ]
    }
}
