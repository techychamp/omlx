import Foundation
import Combine

/// ViewModel for the Compiler Explorer workspace.
/// Note: Due to GUI-002 API Freeze constraints, we cannot add new endpoints
/// for PlanningBundle, ExecutionGraph, OptimizationReports, etc. We rely
/// exclusively on the `DiagnosticsServiceProtocol` to fetch what compiler
/// inspection data is available in the frozen v1 API.
@MainActor
class CompilerViewModel: ObservableObject {
    private let diagnosticsService: DiagnosticsServiceProtocol

    @Published var compilerInspection: CompilerInspection?
    @Published var isLoading = false
    @Published var errorMessage: String?

    init(diagnosticsService: DiagnosticsServiceProtocol) {
        self.diagnosticsService = diagnosticsService
    }

    func load() async {
        isLoading = true
        errorMessage = nil
        do {
            compilerInspection = try await diagnosticsService.getCompilerInspection()
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}
