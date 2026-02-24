import Foundation

public enum ReviewRating: Int, Codable, Sendable {
    case forgot = 0
    case hard = 1
    case good = 2
    case easy = 3
}

public struct ReviewState: Codable, Hashable, Sendable {
    public var easeFactor: Double
    public var intervalDays: Int
    public var repetitions: Int
    public var nextReviewDate: Date

    public init(
        easeFactor: Double = 2.5,
        intervalDays: Int = 1,
        repetitions: Int = 0,
        nextReviewDate: Date = .now
    ) {
        self.easeFactor = easeFactor
        self.intervalDays = intervalDays
        self.repetitions = repetitions
        self.nextReviewDate = nextReviewDate
    }
}

public struct SpacedRepetitionScheduler: Sendable {
    public init() {}

    public func scheduleNext(from state: ReviewState, rating: ReviewRating, now: Date = .now) -> ReviewState {
        var updated = state

        switch rating {
        case .forgot:
            updated.repetitions = 0
            updated.intervalDays = 1
            updated.easeFactor = max(1.3, updated.easeFactor - 0.2)
        case .hard:
            updated.repetitions += 1
            updated.intervalDays = max(1, Int(Double(updated.intervalDays) * 1.2))
            updated.easeFactor = max(1.3, updated.easeFactor - 0.15)
        case .good:
            updated.repetitions += 1
            updated.intervalDays = updated.repetitions <= 1 ? 1 : Int(Double(updated.intervalDays) * updated.easeFactor)
        case .easy:
            updated.repetitions += 1
            updated.easeFactor += 0.1
            updated.intervalDays = max(2, Int(Double(updated.intervalDays) * (updated.easeFactor + 0.15)))
        }

        updated.nextReviewDate = Calendar.current.date(byAdding: .day, value: updated.intervalDays, to: now) ?? now
        return updated
    }
}
