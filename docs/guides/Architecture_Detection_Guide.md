# Architecture Detection Guide

## How it works
`ModelClassifier` infers architecture by parsing `architecture`, `model_type`, or layer keys (like `unet` or `dit`).

## Adding New Architectures
Update `ModelClassifier.classify_architecture` or `classify_family` based on specific metadata heuristics. Do not hardcode repositories.
