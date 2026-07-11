import SwiftUI
import MarkdownUI

struct ConversationView: View {
    @Bindable var vm: GenerationViewModel
    @Environment(\.omlxTheme) private var theme

    @State private var isUserScrollingUp = false

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 16) {
                    if vm.messages.isEmpty && vm.streamingDelta.isEmpty {
                        emptyState
                    } else {
                        ForEach(vm.messages) { msg in
                            MessageRow(message: msg)
                                .id(msg.id)
                                .accessibilityElement(children: .contain)
                                .accessibilityLabel("\(msg.role == "user" ? "Your message" : "Assistant response"): \(msg.content)")
                        }

                        if !vm.streamingDelta.isEmpty {
                            MessageRow(message: ChatMessage(role: "assistant", content: vm.streamingDelta), isStreaming: true)
                                .id("streaming")
                                .accessibilityElement(children: .contain)
                                .accessibilityLabel("Assistant is generating response...")
                        }

                        if let error = vm.error {
                            ErrorRow(error: error)
                                .id("error")
                                .accessibilityElement(children: .combine)
                                .accessibilityLabel("Error: \(error.localizedDescription)")
                        }

                        // Invisible anchor to track bottom
                        Color.clear.frame(height: 1)
                            .id("bottom")
                    }
                }
                .padding()
                // Simple geometry reader based tracking could go here, but for now we'll
                // just rely on the user gesture to pause auto scroll, or we can just
                // unconditionally scroll to bottom if we aren't using a complex tracking system.
                // In macOS SwiftUI, tracking manual scroll is tricky without Introspect,
                // so we will provide the requested logic conceptually by only auto-scrolling
                // if we are actively adding new tokens.
            }
            .accessibilityIdentifier("ConversationScrollView")
            .onChange(of: vm.messages.count) { _, _ in
                if !isUserScrollingUp {
                    if let lastId = vm.messages.last?.id {
                        withAnimation { proxy.scrollTo(lastId, anchor: .bottom) }
                    }
                }
            }
            .onChange(of: vm.streamingDelta) { _, _ in
                if !isUserScrollingUp {
                    withAnimation { proxy.scrollTo("streaming", anchor: .bottom) }
                }
            }
            // Add simultaneous gesture to detect when user initiates a scroll
            .simultaneousGesture(
                DragGesture().onChanged { value in
                    // If user drags down (view moves up), they are scrolling up to history
                    if value.translation.height > 0 {
                        isUserScrollingUp = true
                    } else {
                        isUserScrollingUp = false
                    }
                }
            )
            .onChange(of: vm.isGenerating) { _, isGen in
                if !isGen {
                    // Reset scroll tracking when generation stops
                    isUserScrollingUp = false
                }
            }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Spacer().frame(height: 100)
            Image(systemName: "bubble.left.and.bubble.right")
                .font(.system(size: 48, weight: .light))
                .foregroundColor(theme.textTertiary)
                .accessibilityHidden(true)
            Text("No messages yet")
                .font(.omlxText(16, weight: .medium))
                .foregroundColor(theme.text)
            Text("Start a conversation by typing a message below.")
                .font(.omlxText(13))
                .foregroundColor(theme.textSecondary)
        }
        .frame(maxWidth: .infinity, alignment: .center)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Empty conversation. Start a conversation by typing a message below.")
    }
}

private struct MessageRow: View {
    let message: ChatMessage
    var isStreaming: Bool = false
    @Environment(\.omlxTheme) private var theme

    var isUser: Bool {
        message.role == "user"
    }

    var body: some View {
        HStack {
            if isUser { Spacer(minLength: 40) }

            VStack(alignment: isUser ? .trailing : .leading, spacing: 4) {
                Text(isUser ? "You" : "Assistant")
                    .font(.omlxText(11, weight: .semibold))
                    .foregroundColor(theme.textSecondary)
                    .accessibilityHidden(true)

                Markdown(message.content)
                    .padding(12)
                    .background(isUser ? theme.accent.opacity(0.1) : theme.groupBg)
                    .cornerRadius(8)
                    .overlay(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(isUser ? theme.accent.opacity(0.3) : theme.groupBorder, lineWidth: 1)
                    )
            }

            if !isUser {
                if isStreaming {
                    ProgressView()
                        .controlSize(.small)
                        .padding(.leading, 8)
                        .accessibilityLabel("Loading indicator")
                }
                Spacer(minLength: 40)
            }
        }
    }
}

private struct ErrorRow: View {
    let error: Error
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        HStack {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.red)
                .accessibilityHidden(true)
            Text(error.localizedDescription)
                .font(.omlxText(13))
                .foregroundColor(theme.text)
            Spacer()
        }
        .padding()
        .background(Color.red.opacity(0.1))
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(Color.red.opacity(0.3), lineWidth: 1)
        )
    }
}
