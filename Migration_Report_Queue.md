# Migration Report: Queue
- **New Directory**: `omlx/framework/queue/` containing artifacts, admission, manager, observability, and API.
- **Runtime Update**: `omlx/runtime/session.py` modified to support `from_queue_session`.
- **Backward Compatibility**: Fully backward compatible. Default `RuntimeSession.create()` remains available for paths not yet using the queue.
