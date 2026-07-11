# GUI-004 Execution Timeline Guide

## Logic

The `TimelineView` is architected to display the sequential phases of execution (from planning to backend translation) alongside their respective execution durations (in milliseconds). It is intended to function as a profiling viewer akin to Xcode Instruments.

## Implementation Limitations

Currently, the frozen `v1` DTOs defined in GUI-002 do not supply timeline or phase-duration metrics. The UI component is implemented using a SwiftUI `List`, rendering a static placeholder communicating this data limitation, strictly honoring the mandate not to introduce new API endpoints.
