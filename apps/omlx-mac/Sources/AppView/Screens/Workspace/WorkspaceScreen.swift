import SwiftUI

struct WorkspaceScreen: View {
    @Environment(AppServices.self) private var services
    @Environment(\.omlxTheme) private var theme

    @State private var generationVM: GenerationViewModel?
    @State private var sessionVM: SessionViewModel?

    var body: some View {
        Group {
            if let generationVM, let sessionVM {
                HStack(spacing: 0) {
                    SessionSidebar(vm: sessionVM)
                        .frame(width: 250)
                        .background(theme.windowBg.opacity(0.8))

                    Divider()
                        .background(theme.groupBorder)

                    VStack(spacing: 0) {
                        RuntimeStatusView()
                            .padding(.horizontal)
                            .padding(.vertical, 8)
                            .background(theme.groupBg)
                            .border(width: 1, edges: [.bottom], color: theme.groupBorder)

                        ConversationView(vm: generationVM)
                            .frame(maxWidth: .infinity, maxHeight: .infinity)

                        PromptComposer(vm: generationVM)
                            .padding()
                            .background(theme.groupBg)
                            .border(width: 1, edges: [.top], color: theme.groupBorder)
                    }
                    .frame(maxWidth: .infinity)
                }
                .background(theme.windowBg)
                .onChange(of: sessionVM.activeSessionId) { _, _ in
                    generationVM.clear()
                }
            } else {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .onAppear {
            Task { @MainActor in
                self.generationVM = GenerationViewModel(service: services.generationService)
                self.sessionVM = SessionViewModel(service: services.sessionService)
                await self.sessionVM?.fetchSessions()
            }
        }
    }
}


