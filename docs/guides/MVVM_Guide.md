# MVVM Guide

## ViewModels
- Define state (Idle, Loading, Loaded, Error).
- Perform API calls via injected API Client.
- Transform backend DTOs to view-friendly structures.
- Avoid directly mutating UI framework properties. Use `@MainActor` to bind safely.

## Views
- Listen to `@State` or `@ObservedObject`.
- Focus solely on declarative layout logic.
