import XCTest
@testable import LanguageCore

final class LearningPathServiceTests: XCTestCase {
    func testDailyBudgetStopsAtLimit() {
        let lessons = [
            Lesson(title: "One", level: .a1, estimatedMinutes: 5, tags: []),
            Lesson(title: "Two", level: .a1, estimatedMinutes: 7, tags: []),
            Lesson(title: "Three", level: .a2, estimatedMinutes: 10, tags: [])
        ]

        let progress = UserProgress(selectedLanguage: "Spanish", targetLevel: .b1)
        let sut = LearningPathService()

        let plan = sut.recommendedLessons(from: lessons, progress: progress, dailyTimeBudgetMinutes: 12)

        XCTAssertEqual(plan.count, 2)
        XCTAssertEqual(plan.map(\.title), ["One", "Two"])
    }

    func testStreakResetsAfterGap() {
        let sut = LearningPathService()
        let yesterday = Calendar.current.date(byAdding: .day, value: -2, to: .now)!
        let progress = UserProgress(selectedLanguage: "Japanese", targetLevel: .b2, currentStreak: 10, longestStreak: 10, lastStudyDate: yesterday)

        let updated = sut.updatedStreak(from: progress, now: .now)

        XCTAssertEqual(updated.currentStreak, 1)
        XCTAssertEqual(updated.longestStreak, 10)
    }
}
