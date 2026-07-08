import XCTest
@testable import oMLX

final class DeveloperToolsViewModelTests: XCTestCase {
    func testInitialState() {
        let services = AppServices() // Assuming we can use real or some mock
        let viewModel = DeveloperToolsViewModel(services: services)

        XCTAssertEqual(viewModel.selectedTab, .apiExplorer)
        XCTAssertNil(viewModel.runtimeStatus)
        XCTAssertNil(viewModel.error)
        XCTAssertFalse(viewModel.isLoading)
    }

    func testTabSwitching() {
        let services = AppServices()
        let viewModel = DeveloperToolsViewModel(services: services)

        viewModel.selectedTab = .logExplorer
        XCTAssertEqual(viewModel.selectedTab, .logExplorer)
    }
}
