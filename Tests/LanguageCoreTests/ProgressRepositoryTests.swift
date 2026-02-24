import XCTest
@testable import LanguageCore

final class ProgressRepositoryTests: XCTestCase {
    func testSaveAndLoadRoundTrip() throws {
        let suiteName = "ProgressRepositoryTests-\(UUID().uuidString)"
        guard let defaults = UserDefaults(suiteName: suiteName) else {
            XCTFail("Could not create user defaults suite")
            return
        }

        let repository = ProgressRepository(defaults: defaults)
        let original = UserProgress(selectedLanguage: "French", targetLevel: .c1, currentStreak: 5)

        try repository.save(original)
        let loaded = try repository.load()

        XCTAssertEqual(loaded.selectedLanguage, "French")
        XCTAssertEqual(loaded.targetLevel, .c1)
        XCTAssertEqual(loaded.currentStreak, 5)
    }
}
