import os
import glob

# Remove 'public ' from DTOs and Services
files = glob.glob('Sources/Net/DTO/*.swift') + glob.glob('Sources/Services/*.swift') + glob.glob('Sources/Services/Previews/*.swift') + glob.glob('Tests/oMLXTests/Mocks/*.swift')

for path in files:
    with open(path, 'r') as f:
        content = f.read()
    
    content = content.replace('public struct', 'struct')
    content = content.replace('public let', 'let')
    content = content.replace('public var', 'var')
    content = content.replace('public init', 'init')
    content = content.replace('public protocol', 'protocol')
    content = content.replace('public actor', 'actor')
    content = content.replace('public func', 'func')
    content = content.replace('public nonisolated func', 'nonisolated func')
    
    # In GenerationService, fix the stream signature
    if 'GenerationService.swift' in path:
        content = content.replace('func stream(request: GenerateRequest) -> AsyncThrowingStream', 'func stream(request: GenerateRequest) async throws -> AsyncThrowingStream')
        content = content.replace('nonisolated func stream(request: GenerateRequest) -> AsyncThrowingStream', 'func stream(request: GenerateRequest) async throws -> AsyncThrowingStream')
        # add await client.stream
        content = content.replace('return client.stream(', 'return await client.stream(')
    
    # In MockGenerationService
    if 'MockGenerationService.swift' in path:
        content = content.replace('func stream(request: GenerateRequest) -> AsyncThrowingStream', 'func stream(request: GenerateRequest) async throws -> AsyncThrowingStream')
        content = content.replace('nonisolated func stream(request: GenerateRequest) -> AsyncThrowingStream', 'func stream(request: GenerateRequest) async throws -> AsyncThrowingStream')
    
    # In PreviewMocks
    if 'PreviewMocks.swift' in path:
        content = content.replace('func stream(request: GenerateRequest) -> AsyncThrowingStream', 'func stream(request: GenerateRequest) async throws -> AsyncThrowingStream')
        content = content.replace('nonisolated func stream(request: GenerateRequest) -> AsyncThrowingStream', 'func stream(request: GenerateRequest) async throws -> AsyncThrowingStream')

    with open(path, 'w') as f:
        f.write(content)

print("Fixed access modifiers and stream concurrency.")
