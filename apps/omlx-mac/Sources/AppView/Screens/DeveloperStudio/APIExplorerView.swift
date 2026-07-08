import SwiftUI

struct APIEndpointInfo: Identifiable, Sendable {
    let id = UUID()
    let path: String
    let description: String
    let methods: [String]
    let requestDTO: String?
    let responseDTO: String?
    let streamingSupport: Bool
    let apiVersion: String
}

struct APIExplorerView: View {
    @Environment(\.omlxTheme) private var theme

    let endpoints: [APIEndpointInfo] = [
        APIEndpointInfo(path: "/v1/chat/completions", description: "Core generation and streaming.", methods: ["POST"], requestDTO: "GenerateRequest", responseDTO: "GenerateResponse", streamingSupport: true, apiVersion: "v1"),
        APIEndpointInfo(path: "/v1/models", description: "Model discovery, loading, and unloading.", methods: ["GET", "POST", "DELETE"], requestDTO: "ModelLoadRequest", responseDTO: "ModelInfo", streamingSupport: false, apiVersion: "v1"),
        APIEndpointInfo(path: "/v1/runtime", description: "System status, backend info, and capabilities.", methods: ["GET"], requestDTO: nil, responseDTO: "RuntimeStatus", streamingSupport: false, apiVersion: "v1"),
        APIEndpointInfo(path: "/v1/sessions", description: "Chat session persistence and state.", methods: ["GET", "POST"], requestDTO: "SessionCreateRequest", responseDTO: "SessionInfo", streamingSupport: false, apiVersion: "v1"),
        APIEndpointInfo(path: "/v1/compiler", description: "Graph compilation progress and inspection.", methods: ["GET"], requestDTO: nil, responseDTO: "CompilerInspection", streamingSupport: true, apiVersion: "v1"),
        APIEndpointInfo(path: "/v1/diagnostics", description: "Telemetry (execution, Apple Silicon metrics).", methods: ["GET"], requestDTO: nil, responseDTO: "DiagnosticsInfo", streamingSupport: false, apiVersion: "v1"),
        APIEndpointInfo(path: "/v1/benchmarks", description: "Standardized benchmarking operations.", methods: ["GET", "POST"], requestDTO: "BenchmarkRequest", responseDTO: "BenchmarkReport", streamingSupport: false, apiVersion: "v1")
    ]

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                ForEach(endpoints) { endpoint in
                    EndpointCard(endpoint: endpoint)
                }
            }
            .padding()
        }
    }
}

private struct EndpointCard: View {
    let endpoint: APIEndpointInfo
    @Environment(\.omlxTheme) private var theme

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text(endpoint.path)
                    .font(.headline)
                    .foregroundColor(theme.textPrimary)
                Spacer()
                Text(endpoint.apiVersion)
                    .font(.caption)
                    .padding(4)
                    .background(theme.groupBorder)
                    .cornerRadius(4)
            }

            Text(endpoint.description)
                .font(.subheadline)
                .foregroundColor(theme.textSecondary)

            Divider()

            HStack {
                Text("Methods:")
                    .font(.caption)
                    .foregroundColor(theme.textSecondary)
                ForEach(endpoint.methods, id: \.self) { method in
                    Text(method)
                        .font(.caption)
                        .padding(4)
                        .background(Color.blue.opacity(0.2))
                        .cornerRadius(4)
                }
            }

            if let req = endpoint.requestDTO {
                HStack {
                    Text("Request DTO:")
                        .font(.caption)
                        .foregroundColor(theme.textSecondary)
                    Text(req)
                        .font(.caption.monospaced())
                }
            }

            if let resp = endpoint.responseDTO {
                HStack {
                    Text("Response DTO:")
                        .font(.caption)
                        .foregroundColor(theme.textSecondary)
                    Text(resp)
                        .font(.caption.monospaced())
                }
            }

            HStack {
                Text("Streaming:")
                    .font(.caption)
                    .foregroundColor(theme.textSecondary)
                Text(endpoint.streamingSupport ? "Supported" : "Not Supported")
                    .font(.caption)
                    .foregroundColor(endpoint.streamingSupport ? .green : .red)
            }
        }
        .padding()
        .background(theme.groupBg)
        .cornerRadius(8)
        .overlay(
            RoundedRectangle(cornerRadius: 8)
                .stroke(theme.groupBorder, lineWidth: 1)
        )
    }
}
