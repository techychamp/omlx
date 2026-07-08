# API Integration Report

## Client
The GUI communicates with the oMLX server using a unified API client architecture (likely located in the `Net` folder, e.g., `APIClient.swift`).

## Polling & Status
`MenubarController` periodically polls the server for status and statistics to keep the UI responsive and accurately reflect the backend state without direct coupling.
