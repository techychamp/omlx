# Architecture Diagrams

```mermaid
graph TD
    A[Compiler] --> B[Logical IR]
    B --> C[Lowering]
    C --> D[Physical IR]
    D --> E[Backend]
```
