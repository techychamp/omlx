# Session Lifecycle Diagram

```text
 Client
   |
   +-> stream(session_id)
         |
         v
 StreamingController -> create_session()
         |
         +--> [ SESSION_STARTED ]
         |
 BackendAdapter (Future)
   |
   +--> publish_event(TOKEN_GENERATED) -> Queue -> TokenEmitter -> Client
   +--> publish_event(TOKEN_GENERATED) -> Queue -> TokenEmitter -> Client
   |
   +--> publish_event(COMPLETED) -> Session marked COMPLETED -> TokenEmitter yields None -> Client Stream Ends
```
