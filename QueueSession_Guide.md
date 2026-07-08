# QueueSession Guide
`QueueSession` is a deeply immutable dataclass representing the pre-execution lifecycle of a request.
- Contains the `QueueEntry` (original request and admission time).
- Contains the `QueueDescriptor` (queue configuration).
- Represents state ('queued', 'ready_for_execution').
- Extracted and transferred to a `RuntimeSession` when execution begins.
