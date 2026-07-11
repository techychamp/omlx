# Migration Report

## Transitioning to GUI
No existing CLI or backend code requires migration to run the GUI. The GUI wraps the server process (`ServerProcess.swift`).

## Safety
The Python layer remains completely untainted by Swift-specific types.
