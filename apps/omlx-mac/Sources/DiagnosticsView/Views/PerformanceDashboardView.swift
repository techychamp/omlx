import SwiftUI

struct PerformanceDashboardView: View {
    @StateObject private var viewModel: DiagnosticsViewModel

    init(diagnosticsService: DiagnosticsServiceProtocol) {
        _viewModel = StateObject(wrappedValue: DiagnosticsViewModel(diagnosticsService: diagnosticsService))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                DiagnosticsSummaryCard(viewModel: viewModel)

                DiagnosticsSectionCard(
                    title: "Runtime Metrics",
                    systemImage: "timer",
                    isLoading: viewModel.isLoading,
                    error: viewModel.error(for: .runtime)
                ) {
                    if let metrics = viewModel.executionMetrics {
                        MetricRow(label: "API Version", value: metrics.apiVersion ?? "N/A")
                        MetricRow(label: "Prompt Tokens", value: "\(metrics.promptTokens)")
                        MetricRow(label: "Completion Tokens", value: "\(metrics.completionTokens)")
                        MetricRow(label: "Total Tokens", value: "\(metrics.totalTokens)")
                    } else {
                        Text("No runtime metrics available")
                            .foregroundStyle(.secondary)
                    }
                }

                DiagnosticsSectionCard(
                    title: "Apple Silicon",
                    systemImage: "cpu",
                    isLoading: viewModel.isLoading,
                    error: viewModel.error(for: .apple)
                ) {
                    if let metrics = viewModel.appleMetrics {
                        MetricRow(label: "API Version", value: metrics.apiVersion ?? "N/A")
                        MetricRow(label: "Memory Used", value: "\(metrics.memoryUsed / (1024 * 1024)) MB")
                        MetricRow(label: "ANE Utilization", value: String(format: "%.1f %%", metrics.aneUtilization * 100))
                        MetricRow(label: "GPU Utilization", value: String(format: "%.1f %%", metrics.gpuUtilization * 100))
                    } else {
                        Text("No Apple Silicon metrics available")
                            .foregroundStyle(.secondary)
                    }
                }

                DiagnosticsSectionCard(
                    title: "Benchmark Center",
                    systemImage: "chart.bar",
                    isLoading: viewModel.isLoading,
                    error: viewModel.error(for: .benchmarks)
                ) {
                    if let report = viewModel.benchmarkReport {
                        MetricRow(label: "API Version", value: report.apiVersion ?? "N/A")
                        MetricRow(label: "Throughput", value: String(format: "%.2f", report.throughput))
                        MetricRow(label: "Tokens / Sec", value: String(format: "%.2f", report.tokensPerSecond))
                    } else {
                        Text("No benchmark data available")
                            .foregroundStyle(.secondary)
                    }
                }

                DiagnosticsSectionCard(
                    title: "Diagnostics Explorer",
                    systemImage: "magnifyingglass",
                    isLoading: viewModel.isLoading,
                    error: viewModel.error(for: .explorer)
                ) {
                    if let inspection = viewModel.compilerInspection {
                        MetricRow(label: "API Version", value: inspection.apiVersion ?? "N/A")
                        MetricRow(label: "Compiler Version", value: inspection.compilerVersion)
                        MetricRow(label: "Graph Status", value: inspection.graphStatus)
                    } else {
                        Text("No compiler diagnostics available")
                            .foregroundStyle(.secondary)
                    }
                }

                DiagnosticsSectionCard(
                    title: "Execution Timeline",
                    systemImage: "clock",
                    isLoading: false,
                    error: nil
                ) {
                    Text("Timeline data is not available yet.")
                        .foregroundStyle(.secondary)
                }

                DiagnosticsSectionCard(
                    title: "Resource Dashboard",
                    systemImage: "memorychip",
                    isLoading: viewModel.isLoading,
                    error: viewModel.error(for: .resources)
                ) {
                    if let metrics = viewModel.appleMetrics {
                        MetricRow(label: "Memory Used", value: "\(metrics.memoryUsed / (1024 * 1024)) MB")
                        MetricRow(label: "GPU Utilization", value: String(format: "%.1f %%", metrics.gpuUtilization * 100))
                    } else {
                        Text("No resource data available")
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .padding()
        }
        .task {
            await viewModel.fetchAll()
        }
    }
}

private struct DiagnosticsSummaryCard: View {
    @ObservedObject var viewModel: DiagnosticsViewModel

    private var completedCount: Int {
        [
            viewModel.executionMetrics != nil,
            viewModel.appleMetrics != nil,
            viewModel.benchmarkReport != nil,
            viewModel.compilerInspection != nil
        ].filter { $0 }.count
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Summary", systemImage: "gauge")
                .font(.headline)

            HStack(spacing: 12) {
                SummaryPill(label: "Sections Loaded", value: "\(completedCount)/4", color: .green)
                SummaryPill(label: "Failures", value: "\(viewModel.sectionErrors.count)", color: viewModel.sectionErrors.isEmpty ? .green : .red)
                SummaryPill(label: "State", value: viewModel.isLoading ? "Loading" : "Ready", color: viewModel.isLoading ? .orange : .blue)
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(NSColor.controlBackgroundColor))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}

private struct SummaryPill: View {
    let label: String
    let value: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(.headline)
                .foregroundStyle(color)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct DiagnosticsSectionCard<Content: View>: View {
    let title: String
    let systemImage: String
    let isLoading: Bool
    let error: Error?
    private let content: Content

    init(
        title: String,
        systemImage: String,
        isLoading: Bool,
        error: Error?,
        @ViewBuilder content: () -> Content
    ) {
        self.title = title
        self.systemImage = systemImage
        self.isLoading = isLoading
        self.error = error
        self.content = content()
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Label(title, systemImage: systemImage)
                .font(.headline)

            if isLoading {
                ProgressView("Loading...")
            } else if let error {
                Text("Error: \(error.omlxDescription)")
                    .foregroundStyle(.red)
            } else {
                VStack(alignment: .leading, spacing: 8) {
                    content
                }
            }
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(NSColor.controlBackgroundColor))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }
}
