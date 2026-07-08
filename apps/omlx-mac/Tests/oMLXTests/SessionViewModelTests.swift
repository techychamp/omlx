import XCTest
@testable import oMLX

@MainActor
final class SessionViewModelTests: XCTestCase {
    func testFetchSessions() async {
        let mockService = MockSessionService()
        let vm = SessionViewModel(service: mockService)

        await vm.fetchSessions()

        XCTAssertFalse(vm.sessions.isEmpty)
        XCTAssertEqual(vm.sessions.first?.sessionId, "mock-session-1")
    }

    func testSelectSession() async {
        let mockService = MockSessionService()
        let vm = SessionViewModel(service: mockService)

        vm.selectSession("test-id")
        XCTAssertEqual(vm.activeSessionId, "test-id")
    }

    func testCreateNewSession() async {
        let mockService = MockSessionService()
        let vm = SessionViewModel(service: mockService)

        vm.activeSessionId = "test-id"
        vm.createNewSession()
        XCTAssertNil(vm.activeSessionId)
    }

    func testDeleteSession() async {
        let mockService = MockSessionService()
        let vm = SessionViewModel(service: mockService)
        await vm.fetchSessions()

        XCTAssertEqual(vm.sessions.count, 2)

        vm.activeSessionId = "mock-session-1"
        vm.deleteSession("mock-session-1")

        XCTAssertEqual(vm.sessions.count, 1)
        XCTAssertNil(vm.activeSessionId)
        XCTAssertEqual(vm.sessions.first?.sessionId, "mock-session-2")
    }
}
