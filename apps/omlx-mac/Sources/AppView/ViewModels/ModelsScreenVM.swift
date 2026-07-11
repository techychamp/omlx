import SwiftUI

@MainActor
@Observable
final class ModelsScreenVM {
    private(set) var allModels: [ModelDTO] = []
    var lastError: String?
    /// Library row the user just clicked "trash" on; non-nil drives the
    /// confirmation dialog. Cleared on cancel or after delete completes.
    var pendingRemoveID: String?
    /// While a delete is in flight, the row shows a spinner instead of the
    /// trash glyph and the whole row's button-stack is disabled to prevent
    /// double-tap deletes against a model the server is still unloading.
    private(set) var deletingID: String?

    @ObservationIgnored
    private var modelManagementService: ModelManagementServiceProtocol?
    @ObservationIgnored
    private var pollTask: Task<Void, Never>?

    var activeModels: [ModelDTO] {
        allModels.filter { $0.loaded || $0.isLoading }
    }
    var libraryModels: [ModelDTO] { allModels }

    func start(modelManagementService: ModelManagementServiceProtocol) async {
        self.modelManagementService = modelManagementService
        pollTask?.cancel()
        pollTask = Task { [weak self] in
            while !Task.isCancelled {
                guard let self else { return }
                await self.refresh()
                try? await Task.sleep(for: .seconds(2))
            }
        }
    }

    func stop() {
        pollTask?.cancel()
        pollTask = nil
    }

    func load(id: String) {
        Task { [weak self] in
            guard let self, let modelManagementService = self.modelManagementService else { return }
            do {
                _ = try await modelManagementService.loadModel(id: id)
                await self.refresh()
            } catch {
                self.lastError = error.omlxDescription
            }
        }
    }

    func unload(id: String) {
        Task { [weak self] in
            guard let self, let modelManagementService = self.modelManagementService else { return }
            do {
                _ = try await modelManagementService.unloadModel(id: id)
                await self.refresh()
            } catch {
                self.lastError = error.omlxDescription
            }
        }
    }

    func remove(id: String) {
        pendingRemoveID = nil
        deletingID = id
        Task { [weak self] in
            guard let self, let modelManagementService = self.modelManagementService else { return }
            defer { Task { @MainActor [weak self] in self?.deletingID = nil } }
            do {
                _ = try await modelManagementService.deleteHFModel(modelName: id)
                await self.refresh()
                self.lastError = nil
            } catch {
                self.lastError = error.omlxDescription
            }
        }
    }

    private func refresh() async {
        guard let modelManagementService else { return }
        do {
            self.allModels = sortModelsByName(try await modelManagementService.listModels().models)
            self.lastError = nil
        } catch {
            self.lastError = error.omlxDescription
        }
    }

}
