# Graph Export Documentation

The toolkit supports exporting raw dictionary data and graph views into various formats.

## Supported Formats
- **JSON / YAML**: Best for machine-readable state inspection and diffing.
- **GraphViz DOT**: Standard for complex graph layouts and dependency mapping.
- **Mermaid.js**: Ideal for embedding directly into GitHub markdown or PR comments.
- **PlantUML**: Standardized diagram generation.
- **Markdown**: Generates developer-readable hierarchical lists.

## Architecture
All exporters extend `BaseExporter` and implement `def export(self, data: dict, **kwargs) -> str`. This allows new formats to be added easily.
