# Desktop Shell Report

## Window Management
The application starts suppressed without a window (`.defaultLaunchBehavior(.suppressed)`).
It relies on `AppDelegate` to manage the lifecycle of the main window (`NSWindow`) and the Menubar app status.

## Layout & Workspace
The workspace is built using SwiftUI's `NavigationSplitView`.
The sidebar provides access to different sections (e.g., Status, Server, Models) defined in `AppSection`.
