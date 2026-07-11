import Foundation
import SwiftUI

@MainActor
@Observable
final class GenerationViewModel {
    let service: GenerationServiceProtocol

    var currentModel: String = "omlx-default"
    var messages: [ChatMessage] = []

    var currentDraft: String = ""
    var isGenerating: Bool = false
    var streamingDelta: String = ""
    var error: Error?

    private var streamTask: Task<Void, Never>?

    init(service: GenerationServiceProtocol) {
        self.service = service
    }

    func send() async {
        guard !isGenerating else { return } // Prevent concurrent sends

        let draft = currentDraft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !draft.isEmpty else { return }

        let message = ChatMessage(role: "user", content: draft)
        messages.append(message)
        currentDraft = ""
        error = nil

        await streamResponse()
    }

    func streamResponse() async {
        isGenerating = true
        streamingDelta = ""

        let request = GenerateRequest(model: currentModel, messages: messages, stream: true)

        streamTask = Task { [weak self] in
            guard let self = self else { return }
            do {
                let stream = try await self.service.stream(request: request)
                for try await chunk in stream {
                    if Task.isCancelled { break }
                    if let content = chunk.choices.first?.delta.content {
                        await MainActor.run {
                            self.streamingDelta += content
                        }
                    }
                }

                if !Task.isCancelled {
                    await MainActor.run {
                        let finalMessage = ChatMessage(role: "assistant", content: self.streamingDelta)
                        self.messages.append(finalMessage)
                        self.streamingDelta = ""
                    }
                }
            } catch {
                await MainActor.run {
                    self.error = error
                    self.streamingDelta = "" // Clear stale partials on error
                }
            }

            await MainActor.run {
                self.isGenerating = false
                self.streamTask = nil
            }
        }
    }

    func stopGeneration() {
        streamTask?.cancel()
        streamTask = nil
        isGenerating = false

        if !streamingDelta.isEmpty {
            let finalMessage = ChatMessage(role: "assistant", content: streamingDelta)
            messages.append(finalMessage)
            streamingDelta = "" // Clear after cancellation logic
        }
    }

    func clear() {
        stopGeneration()
        messages.removeAll()
        error = nil
        streamingDelta = ""
    }
}
