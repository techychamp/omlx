# Synchronization Guide

## Synchronization Nodes
Synchronization in batch processing is realized explicitly within the `BatchSynchronizationGraph` as dedicated synchronization nodes. The Execution Engine must respect these barriers but does not generate them.
