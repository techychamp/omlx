// Regression coverage for the menubar-shows-stale-port bug.
//
// Before the fix, MenubarController captured `config: AppConfig` by value
// at init and rendered `config.port` in the running-status header / port
// alert / Chat URL. The user-facing flow:
//   1. ServerScreen's Apply commits a new port via
//      `AppServices.applyServerEndpoint(port:)`.
//   2. AppServices calls `server.reconfigure(port:)` and restarts the
//      ServerProcess on the new port.
//   3. The server transitions to `.running(newPid)`; the menubar's
//      stateDidChange observer fires `refreshMenuState()`.
//   4. `refreshMenuState()` rebuilds the header — and read the OLD port
//      from the stale `config` snapshot. The user saw `:8080` after
//      changing to `:8964`.
//
// Fix: `MenubarController.displayPort(server:fallback:)` sources from
// the live server (which `reconfigure(port:)` updates), falling back to
// the captured config snapshot only when there is no server (bootstrap
// failed). These tests exercise the helper directly — instantiating the
// full controller in a unit test would require a live `NSStatusBar`.

import Foundation
import XCTest
@testable import oMLX

@MainActor
final class MenubarControllerPortTests: XCTestCase {

    /// Test-only PythonRuntime. ServerProcess holds it but doesn't
    /// dereference until `start()` — these tests never start, they just
    /// read `.port` / `.host` after `reconfigure`.
    private func makeRuntime() -> PythonRuntime {
        PythonRuntime(
            executable: URL(fileURLWithPath: "/usr/bin/true"),
            homebrewPaths: [],
            pythonPath: [],
            pythonHome: nil,
            isBundled: false
        )
    }

    func testSpawnEnvironmentAdvertisesMenubarSupervisor() {
        let env = makeRuntime().makeEnvironment()
        XCTAssertEqual(env["OMLX_SUPERVISED"], "menubar")
    }

    func testServerStartAttachesToExistingOMLXServerOnConfiguredPort() async throws {
        let healthServer = try TinyHealthServer()
        try healthServer.start()
        addTeardownBlock {
            healthServer.stop()
        }

        let tempBase = FileManager.default.temporaryDirectory
            .appendingPathComponent("ServerAttachTests-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: tempBase, withIntermediateDirectories: true)
        addTeardownBlock {
            try? FileManager.default.removeItem(at: tempBase)
        }

        let server = ServerProcess(
            runtime: makeRuntime(),
            bindAddress: "127.0.0.1",
            port: healthServer.port,
            basePath: tempBase
        )

        let result = try server.start()

        if case .alreadyRunning = result {
            // Expected.
        } else {
            XCTFail("Expected .alreadyRunning when /health already responds, got \(result)")
        }
        if case .running = server.state {
            // Expected: the app attached to the healthy server instead of
            // reporting a port conflict and asking the user to start again.
        } else {
            XCTFail("Expected .running after attaching to existing server, got \(server.state)")
        }
        XCTAssertNil(server.pid, "Attached external servers are tracked by health, not owned as child processes.")

        await server.stop(timeout: 1)
    }

    // MARK: - displayPort

    func testDisplayPortFallsBackToConfigWhenNoServer() {
        XCTAssertEqual(
            MenubarController.displayPort(server: nil, fallback: 8080),
            8080,
            "With no server (bootstrap failed), the displayed port must come from the AppConfig snapshot."
        )
    }

    func testDisplayPortPrefersLiveServer() {
        let server = ServerProcess(runtime: makeRuntime(), port: 8888)
        XCTAssertEqual(
            MenubarController.displayPort(server: server, fallback: 8080),
            8888,
            "When a server is present, its `port` is authoritative — `fallback` is only for the no-server case."
        )
    }

    func testDisplayPortFollowsReconfigure() throws {
        // The original bug: menubar's `config.port` snapshot never sees
        // this change, so the running-header text keeps showing 8080.
        let server = ServerProcess(runtime: makeRuntime(), port: 8080)
        try server.reconfigure(port: 8964)
        XCTAssertEqual(
            MenubarController.displayPort(server: server, fallback: 8080),
            8964,
            "After Server screen's Apply commits a new port (which calls server.reconfigure(port:)), the menubar must source from the live server."
        )
    }

    // MARK: - displayHost

    func testDisplayHostFallsBackToConfigWhenNoServer() {
        XCTAssertEqual(
            MenubarController.displayHost(server: nil, fallback: "127.0.0.1"),
            "127.0.0.1"
        )
    }

    func testDisplayHostPrefersLiveServer() {
        let server = ServerProcess(runtime: makeRuntime(), bindAddress: "127.0.0.1", port: 8080)
        XCTAssertEqual(
            MenubarController.displayHost(server: server, fallback: "127.0.0.1"),
            "127.0.0.1"
        )
    }

    func testDisplayHostUsesServerConnectableHost() {
        let server = ServerProcess(runtime: makeRuntime(), bindAddress: "0.0.0.0", port: 8080)
        XCTAssertEqual(
            MenubarController.displayHost(server: server, fallback: "127.0.0.1"),
            "127.0.0.1",
            "ServerProcess.host returns the connectable host (0.0.0.0 → 127.0.0.1)."
        )
    }

    func testDisplayHostFollowsReconfigure() throws {
        let server = ServerProcess(runtime: makeRuntime(), bindAddress: "127.0.0.1", port: 8080)
        try server.reconfigure(bindAddress: "localhost")
        XCTAssertEqual(
            MenubarController.displayHost(server: server, fallback: "127.0.0.1"),
            "127.0.0.1",
            "Listen Address changes propagate through ServerProcess.host, which returns the connectable loopback host."
        )
    }

    func testDisplayHostHandlesCommaSeparatedBindAddress() throws {
        let server = ServerProcess(
            runtime: makeRuntime(),
            bindAddress: "0.0.0.0,127.0.0.1",
            port: 8080
        )
        XCTAssertEqual(
            MenubarController.displayHost(server: server, fallback: "127.0.0.1"),
            "127.0.0.1",
            "The menubar should use the first configured bind host and normalize wildcards before building URLs."
        )
    }

    // MARK: - webAdminURL
    //
    // The "Open Web Dashboard" menubar item routes through the server's
    // /admin/auto-login endpoint so the dashboard opens without the manual
    // login form. The action method itself needs a live NSStatusBar, so we
    // test the pure URL builder it delegates to.

    func testWebAdminURLUsesAutoLoginWithRedirect() throws {
        let url = try XCTUnwrap(
            MenubarController.webAdminURL(host: "127.0.0.1", port: 8000, apiKey: "secret")
        )
        let comps = try XCTUnwrap(URLComponents(url: url, resolvingAgainstBaseURL: false))
        XCTAssertEqual(comps.scheme, "http")
        XCTAssertEqual(comps.host, "127.0.0.1")
        XCTAssertEqual(comps.port, 8000)
        XCTAssertEqual(comps.path, "/admin/auto-login")
        let items = comps.queryItems ?? []
        XCTAssertEqual(items.first { $0.name == "redirect" }?.value, "/admin/dashboard")
        XCTAssertEqual(items.first { $0.name == "key" }?.value, "secret")
    }

    func testWebAdminURLBuildsIPv6Host() throws {
        let url = try XCTUnwrap(
            MenubarController.webAdminURL(host: "[::1]", port: 8000, apiKey: nil)
        )
        XCTAssertTrue(url.absoluteString.hasPrefix("http://[::1]:8000/admin/auto-login"))
    }

    func testWebAdminURLPercentEncodesKey() throws {
        // A key with URL-reserved characters must survive intact — raw
        // string interpolation would corrupt it; URLComponents encodes it.
        let url = try XCTUnwrap(
            MenubarController.webAdminURL(host: "127.0.0.1", port: 8000, apiKey: "a+b/c&d")
        )
        // The decoded query item value round-trips to the original key.
        let comps = try XCTUnwrap(URLComponents(url: url, resolvingAgainstBaseURL: false))
        XCTAssertEqual(comps.queryItems?.first { $0.name == "key" }?.value, "a+b/c&d")
        // And the raw URL string carries the encoded form, not the literal.
        XCTAssertTrue(url.absoluteString.contains("key=a%2Bb/c%26d"),
                      "key should be percent-encoded in the URL string, got \(url.absoluteString)")
    }

    func testWebAdminURLOmitsKeyWhenMissing() throws {
        for key in [nil, ""] as [String?] {
            let url = try XCTUnwrap(
                MenubarController.webAdminURL(host: "127.0.0.1", port: 8000, apiKey: key)
            )
            let comps = try XCTUnwrap(URLComponents(url: url, resolvingAgainstBaseURL: false))
            XCTAssertNil(comps.queryItems?.first { $0.name == "key" },
                         "empty/nil key must not emit a key= param (server redirects to login instead)")
            XCTAssertEqual(comps.queryItems?.first { $0.name == "redirect" }?.value,
                           "/admin/dashboard")
        }
    }

    // MARK: - menuAvailability

    func testMenuAvailabilityKeepsSettingsEnabledWhenServerIsOffline() {
        for state in [ServerProcess.State.stopped, .failed(message: "Port 8000 in use")] {
            let availability = MenubarController.menuAvailability(for: state)
            XCTAssertTrue(availability.settings)
            XCTAssertFalse(availability.webDashboard)
            XCTAssertFalse(availability.chat)
        }
    }

    func testMenuAvailabilityEnablesBrowserItemsOnlyWhenRunning() {
        let availability = MenubarController.menuAvailability(for: .running(pid: 123))
        XCTAssertTrue(availability.settings)
        XCTAssertTrue(availability.webDashboard)
        XCTAssertTrue(availability.chat)
    }

    func testMenuAvailabilityKeepsBrowserItemsDisabledDuringTransitions() {
        let states: [ServerProcess.State] = [
            .starting,
            .stopping,
            .unresponsive(pid: 123),
        ]

        for state in states {
            let availability = MenubarController.menuAvailability(for: state)
            XCTAssertTrue(availability.settings)
            XCTAssertFalse(availability.webDashboard)
            XCTAssertFalse(availability.chat)
        }
    }

    // MARK: - failure alerts

    func testGenericFailureAlertSkipsPortConflictMessages() {
        XCTAssertFalse(
            MenubarController.shouldShowGenericFailureAlert(message: "Port 8000 in use")
        )
        XCTAssertTrue(
            MenubarController.shouldShowGenericFailureAlert(
                message: "Server exited with code 1 during startup"
            )
        )
    }

    func testAccessFailureHintDetectsPermissionErrors() {
        XCTAssertNotNil(
            MenubarController.accessFailureHint(
                message: "Server exited with code 1 during startup",
                logTail: "PermissionError: [Errno 1] Operation not permitted"
            )
        )
        XCTAssertNil(
            MenubarController.accessFailureHint(
                message: "Server exited with code 1 during startup",
                logTail: "ValueError: no models found"
            )
        )
    }
}

private final class TinyHealthServer: @unchecked Sendable {
    let port: Int
    private let fd: Int32
    private let queue = DispatchQueue(label: "TinyHealthServer")

    init() throws {
        let socketFD = socket(AF_INET, SOCK_STREAM, 0)
        guard socketFD >= 0 else {
            throw POSIXError(.EIO)
        }

        var reuse: Int32 = 1
        setsockopt(socketFD, SOL_SOCKET, SO_REUSEADDR, &reuse, socklen_t(MemoryLayout<Int32>.size))

        var addr = sockaddr_in()
        addr.sin_family = sa_family_t(AF_INET)
        addr.sin_port = 0
        addr.sin_addr.s_addr = inet_addr("127.0.0.1")

        let size = socklen_t(MemoryLayout<sockaddr_in>.size)
        let bound = withUnsafePointer(to: &addr) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                Darwin.bind(socketFD, $0, size)
            }
        }
        guard bound == 0 else {
            close(socketFD)
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }

        var picked = sockaddr_in()
        var pickedSize = socklen_t(MemoryLayout<sockaddr_in>.size)
        let got = withUnsafeMutablePointer(to: &picked) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                Darwin.getsockname(socketFD, $0, &pickedSize)
            }
        }
        guard got == 0 else {
            close(socketFD)
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }
        fd = socketFD
        port = Int(UInt16(bigEndian: picked.sin_port))
    }

    func start() throws {
        guard listen(fd, 8) == 0 else {
            throw POSIXError(POSIXErrorCode(rawValue: errno) ?? .EIO)
        }

        queue.async { [fd] in
            while true {
                let client = accept(fd, nil, nil)
                if client < 0 {
                    break
                }
                var buffer = [UInt8](repeating: 0, count: 1024)
                let bufferCount = buffer.count
                _ = buffer.withUnsafeMutableBytes {
                    Darwin.read(client, $0.baseAddress, bufferCount)
                }
                let response = """
                HTTP/1.1 200 OK\r
                Content-Length: 20\r
                Content-Type: application/json\r
                Connection: close\r
                \r
                {"status":"healthy"}
                """
                response.withCString {
                    _ = Darwin.write(client, $0, strlen($0))
                }
                close(client)
            }
        }
    }

    func stop() {
        close(fd)
    }
}
