# Synchronization Guide

Explains barriers and synchronization points in the phase graph.
## Synchronization Nodes
Synchronization in batch processing is realized explicitly within the `BatchSynchronizationGraph` as dedicated synchronization nodes. The Execution Engine must respect these barriers but does not generate them.
