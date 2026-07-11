import SwiftUI

struct ModelManagementView: View {
    let services: AppServices
    
    @State private var viewModel: ModelManagementViewModel
    @Environment(\.omlxTheme) private var theme
    
    init(services: AppServices) {
        self.services = services
        self._viewModel = State(initialValue: ModelManagementViewModel(service: services.modelManagementService))
    }
    
    var body: some View {
        VStack(spacing: 0) {
            toolbar
            
            if viewModel.isLoading {
                ProgressView()
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .accessibilityLabel("Loading models")
            } else if let error = viewModel.errorMessage {
                VStack(spacing: 12) {
                    Image(systemName: "exclamationmark.triangle")
                        .font(.largeTitle)
                        .foregroundStyle(.red)
                    Text(error)
                        .font(.omlxText(14))
                        .foregroundStyle(theme.text)
                        .multilineTextAlignment(.center)
                }
                .accessibilityElement(children: .combine)
                .accessibilityLabel("Error loading models: \(error)")
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                modelList
            }
        }
        .task {
            await viewModel.loadModels()
        }
    }
    
    private var toolbar: some View {
        HStack(spacing: 16) {
            TextField("Search models...", text: $viewModel.searchQuery)
                .textFieldStyle(.roundedBorder)
                .frame(maxWidth: 300)
                .accessibilityLabel("Search models")
            
            Picker("Sort", selection: $viewModel.sortOrder) {
                ForEach(ModelManagementViewModel.SortOrder.allCases) { order in
                    Text(order.rawValue).tag(order)
                }
            }
            .pickerStyle(.menu)
            .frame(width: 150)
            .accessibilityLabel("Sort models")
            
            Spacer()
        }
        .padding()
        .background(theme.windowBg)
        .border(width: 1, edges: [.bottom], color: theme.groupBorder)
    }
    
    private var modelList: some View {
        let models = viewModel.filteredAndSortedModels
        return Group {
            if models.isEmpty {
                VStack(spacing: 12) {
                    Image(systemName: "cube.transparent")
                        .font(.system(size: 40))
                        .foregroundStyle(theme.textTertiary)
                    Text(viewModel.searchQuery.isEmpty ? "No models available" : "No results for \"\(viewModel.searchQuery)\"")
                        .font(.omlxText(14))
                        .foregroundStyle(theme.textSecondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .accessibilityElement(children: .combine)
                .accessibilityLabel(viewModel.searchQuery.isEmpty ? "No models available" : "No results found for \(viewModel.searchQuery)")
            } else {
                ScrollView {
                    LazyVStack(spacing: 16) {
                        ForEach(models, id: \.id) { model in
                            ModelCard(model: model)
                        }
                    }
                    .padding()
                }
            }
        }
    }
}

private struct ModelCard: View {
    let model: ModelInfo
    
    @Environment(\.omlxTheme) private var theme
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(model.id)
                    .font(.omlxText(16, weight: .semibold))
                    .foregroundStyle(theme.text)
                Spacer()
                StatusBadge(status: model.status)
            }
            .accessibilityElement(children: .combine)
            .accessibilityLabel("\(model.id), status: \(model.status.label)")
            
            Divider()
            
            VStack(alignment: .leading, spacing: 8) {
                Text("Metadata")
                    .font(.omlxText(13, weight: .semibold))
                    .foregroundStyle(theme.textSecondary)
                if let apiVersion = model.apiVersion {
                    ModelInfoRow(label: "API Version", value: apiVersion)
                }
                if model.rawId != model.id {
                    ModelInfoRow(label: "Model ID", value: model.rawId)
                }
                if let engineType = model.engineType, !engineType.isEmpty {
                    ModelInfoRow(label: "Engine", value: engineType)
                }
                if let modelType = model.modelType, !modelType.isEmpty {
                    ModelInfoRow(label: "Model Type", value: modelType)
                }
                if let configModelType = model.configModelType, !configModelType.isEmpty {
                    ModelInfoRow(label: "Config Type", value: configModelType)
                }
                if let context = model.maxContextWindow {
                    ModelInfoRow(label: "Context Length", value: "\(context) tokens")
                }
                if let maxTokens = model.maxTokens {
                    ModelInfoRow(label: "Max Tokens", value: "\(maxTokens)")
                }
                if let actualSize = model.actualSize, !actualSize.isEmpty {
                    ModelInfoRow(label: "Size", value: actualSize)
                } else if let estimatedSize = model.estimatedSize, !estimatedSize.isEmpty {
                    ModelInfoRow(label: "Estimated Size", value: estimatedSize)
                }
                if let sourceType = model.sourceType, !sourceType.isEmpty {
                    ModelInfoRow(label: "Source", value: sourceType)
                }
                if let repo = model.sourceRepoId, !repo.isEmpty {
                    ModelInfoRow(label: "Repository", value: repo)
                }
                if let path = model.modelPath, !path.isEmpty {
                    ModelInfoRow(label: "Path", value: path)
                }
                ModelInfoRow(label: "Pinned", value: model.pinned == true ? "Yes" : "No")
                ModelInfoRow(label: "Default", value: model.isDefault == true ? "Yes" : "No")
            }
        }
        .padding()
        .background(theme.groupBg)
        .clipShape(RoundedRectangle(cornerRadius: 8))
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(theme.groupBorder, lineWidth: 1)
        )
    }
}

private struct StatusBadge: View {
    let status: ModelInfo.Status

    private var color: Color {
        switch status {
        case .loaded: return .green
        case .loading: return .orange
        case .available: return .blue
        }
    }

    var body: some View {
        Text(status.label)
            .font(.system(size: 10, weight: .bold))
            .padding(.horizontal, 6)
            .padding(.vertical, 2)
            .background(color.opacity(0.2))
            .foregroundStyle(color)
            .clipShape(Capsule())
    }
}

private struct ModelInfoRow: View {
    let label: String
    let value: String
    
    @Environment(\.omlxTheme) private var theme
    
    var body: some View {
        HStack(alignment: .top) {
            Text(label)
                .font(.omlxText(13, weight: .medium))
                .foregroundStyle(theme.textSecondary)
                .frame(width: 120, alignment: .leading)
            Text(value)
                .font(.omlxText(13))
                .foregroundStyle(theme.text)
        }
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(label): \(value)")
    }
}

// Helper to apply border to specific edges
extension View {
    func border(width: CGFloat, edges: [Edge], color: Color) -> some View {
        overlay(EdgeBorder(width: width, edges: edges).foregroundColor(color))
    }
}

private struct EdgeBorder: Shape {
    var width: CGFloat
    var edges: [Edge]
    
    func path(in rect: CGRect) -> Path {
        var path = Path()
        for edge in edges {
            var x: CGFloat {
                switch edge {
                case .top, .bottom, .leading: return rect.minX
                case .trailing: return rect.maxX - width
                }
            }
            
            var y: CGFloat {
                switch edge {
                case .top, .leading, .trailing: return rect.minY
                case .bottom: return rect.maxY - width
                }
            }
            
            var w: CGFloat {
                switch edge {
                case .top, .bottom: return rect.width
                case .leading, .trailing: return width
                }
            }
            
            var h: CGFloat {
                switch edge {
                case .top, .bottom: return width
                case .leading, .trailing: return rect.height
                }
            }
            path.addRect(CGRect(x: x, y: y, width: w, height: h))
        }
        return path
    }
}
