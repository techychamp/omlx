# Future Distributed Queue Guide
The QUEUE-001 framework was designed to support distributed queues naturally.
- The `QueueDescriptor` includes a `distributed` flag.
- Because `QueueSession` and `QueueEntry` are deeply immutable, they can be easily serialized and passed across node boundaries.
- Future distributed scheduling can build upon `QueueManager`'s dequeue mechanism without architectural redesign.
