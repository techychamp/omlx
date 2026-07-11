# Fusion Opportunity Report

Current fusion discovery operates statelessly on `GraphAnalysisReport`.
Future opportunities can be added to the analyzer purely as declarative logic:
- QKV Fusion
- MLP + Activation
- Rotary Embedding Fusion
- KV Cache updating

Because `FusionAnalyzer` is metadata-driven, hardware-specific considerations are routed through existing descriptor mechanisms.
