# Dependency Injection Guide

## AppServices
`AppServices` is instantiated once in `AppDelegate` and injected globally using `.environment()`. All network clients and shared preferences exist inside it. ViewModels receive `AppServices` (or specific children) in their init.
