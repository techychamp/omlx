# Thread Safety Report
All added capabilities (descriptors, cost models, constraints, scoring results) are implemented using Python `@dataclass(frozen=True)` and `MappingProxyType`. This ensures strict deep immutability and complete thread-safety without requiring locks during read operations.
