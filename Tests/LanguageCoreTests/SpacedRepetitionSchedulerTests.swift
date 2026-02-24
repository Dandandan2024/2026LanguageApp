import XCTest
@testable import LanguageCore

final class SpacedRepetitionSchedulerTests: XCTestCase {
    func testForgotAnswerResetsInterval() {
        let scheduler = SpacedRepetitionScheduler()
        let state = ReviewState(easeFactor: 2.3, intervalDays: 8, repetitions: 4, nextReviewDate: .now)

        let next = scheduler.scheduleNext(from: state, rating: .forgot, now: .now)

        XCTAssertEqual(next.intervalDays, 1)
        XCTAssertEqual(next.repetitions, 0)
        XCTAssertLessThan(next.easeFactor, state.easeFactor)
    }

    func testEasyAnswerExpandsInterval() {
        let scheduler = SpacedRepetitionScheduler()
        let state = ReviewState(easeFactor: 2.5, intervalDays: 5, repetitions: 3, nextReviewDate: .now)

        let next = scheduler.scheduleNext(from: state, rating: .easy, now: .now)

        XCTAssertGreaterThan(next.intervalDays, state.intervalDays)
        XCTAssertGreaterThan(next.easeFactor, state.easeFactor)
    }
}
