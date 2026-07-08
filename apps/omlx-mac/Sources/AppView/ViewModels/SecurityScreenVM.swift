import SwiftUI

@MainActor
@Observable
final class SecurityScreenVM {
    var apiKeySet: Bool = false
    var apiKey: String?
    var skipApiKeyVerification: Bool = false
    var subKeys: [SubKeyDTO] = []
    var lastError: String?

    func bind<T: Equatable>(
        _ binding: Binding<T>,
        save: @escaping () -> Void
    ) -> Binding<T> {
        Binding(
            get: { binding.wrappedValue },
            set: { newValue in
                let changed = binding.wrappedValue != newValue
                binding.wrappedValue = newValue
                if changed { save() }
            }
        )
    }

    func load(platformService: PlatformServiceProtocol) async {
        do {
            let settings = try await platformService.getGlobalSettings()
            self.apiKeySet = settings.auth?.apiKeySet ?? false
            self.apiKey = settings.auth?.apiKey
            self.skipApiKeyVerification = settings.auth?.skipApiKeyVerification ?? false
            self.subKeys = settings.auth?.subKeys ?? []
            self.lastError = nil
        } catch {
            self.lastError = error.omlxDescription
        }
    }

    func setupApiKey(key: String, confirm: String, platformService: PlatformServiceProtocol) async -> Bool {
        do {
            _ = try await platformService.setupApiKey(key, confirm: confirm)
            // Re-bootstrap the client so subsequent /admin/api/* calls auth
            // with the new key.
            await platformService.updateClientAuth(apiKey: key)
            await load(platformService: platformService)
            return true
        } catch {
            self.lastError = error.omlxDescription
            return false
        }
    }

    /// Unified write path for the editor row. Routes through /setup-api-key
    /// for first-time setup (server rejects the PATCH path when no key is
    /// configured) and through PATCH /global-settings for updates.
    func applyApiKey(_ key: String, platformService: PlatformServiceProtocol) async -> Bool {
        if apiKeySet {
            do {
                _ = try await platformService.updateGlobalSettings(
                    GlobalSettingsPatch(apiKey: key)
                )
                await platformService.updateClientAuth(apiKey: key)
                await load(platformService: platformService)
                return true
            } catch {
                self.lastError = error.omlxDescription
                return false
            }
        } else {
            // First-time setup: the dedicated endpoint requires a confirm
            // value, which the editor row collapses into a single field. We
            // mirror the draft as the confirm so the server-side equality
            // check passes — typo protection lives in the field's own
            // show/copy affordances now, not in a duplicate input.
            return await setupApiKey(key: key, confirm: key, platformService: platformService)
        }
    }

    func saveSkipApiKeyVerification(platformService: PlatformServiceProtocol) async {
        do {
            _ = try await platformService.updateGlobalSettings(
                GlobalSettingsPatch(skipApiKeyVerification: skipApiKeyVerification)
            )
            self.lastError = nil
        } catch {
            self.lastError = error.omlxDescription
        }
    }

    func createSubKey(key: String, name: String, platformService: PlatformServiceProtocol) async -> Bool {
        do {
            _ = try await platformService.createSubKey(key: key, name: name)
            await load(platformService: platformService)
            return true
        } catch {
            self.lastError = error.omlxDescription
            return false
        }
    }

    func deleteSubKey(key: String, platformService: PlatformServiceProtocol) async {
        do {
            _ = try await platformService.deleteSubKey(key: key)
            await load(platformService: platformService)
        } catch {
            self.lastError = error.omlxDescription
        }
    }

}
