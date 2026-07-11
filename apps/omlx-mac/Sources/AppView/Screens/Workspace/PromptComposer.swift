import SwiftUI

struct PromptComposer: View {
    @Bindable var vm: GenerationViewModel
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        HStack(alignment: .bottom, spacing: 12) {
            TextField("Message...", text: $vm.currentDraft, axis: .vertical)
                .textFieldStyle(.plain)
                .font(.omlxText(14))
                .lineLimit(1...8)
                .padding(12)
                .background(theme.windowBg)
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(theme.groupBorder, lineWidth: 1)
                )
                .accessibilityLabel("Message input")
                .accessibilityHint("Type your message to the AI assistant. Press Enter to send.")
                .accessibilityIdentifier("PromptComposerTextField")
                .onSubmit {
                    if !vm.currentDraft.isEmpty && !vm.isGenerating {
                        Task { await vm.send() }
                    }
                }

            if vm.isGenerating {
                Button(action: {
                    vm.stopGeneration()
                }) {
                    Image(systemName: "stop.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(theme.accent)
                }
                .buttonStyle(.plain)
                .padding(.bottom, 8)
                .accessibilityLabel("Stop Generation")
                .accessibilityHint("Interrupts the ongoing AI response.")
                .accessibilityIdentifier("StopGenerationButton")
            } else {
                Button(action: {
                    Task { await vm.send() }
                }) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.system(size: 24))
                        .foregroundColor(vm.currentDraft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? theme.textTertiary : theme.accent)
                }
                .buttonStyle(.plain)
                .disabled(vm.currentDraft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                .padding(.bottom, 8)
                .accessibilityLabel("Send Message")
                .accessibilityHint("Sends your drafted message to the AI assistant.")
                .accessibilityIdentifier("SendMessageButton")
            }
        }
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("PromptComposer")
    }
}
