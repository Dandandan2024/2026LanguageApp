import Foundation

public struct LearningPathService: Sendable {
    public init() {}

    public func recommendedLessons(
        from catalog: [Lesson],
        progress: UserProgress,
        dailyTimeBudgetMinutes: Int
    ) -> [Lesson] {
        let unlocked = catalog
            .filter { !$0.tags.contains("premium-only") }
            .filter { !$0.tags.contains("advanced") || progress.targetLevel.rawValue >= CEFRLevel.b1.rawValue }
            .filter { !progress.completedLessonIDs.contains($0.id) }
            .sorted { lhs, rhs in
                if lhs.level == rhs.level {
                    return lhs.estimatedMinutes < rhs.estimatedMinutes
                }
                return lhs.level.rawValue < rhs.level.rawValue
            }

        var total = 0
        return unlocked.filter { lesson in
            guard total + lesson.estimatedMinutes <= dailyTimeBudgetMinutes else {
                return false
            }
            total += lesson.estimatedMinutes
            return true
        }
    }

    public func updatedStreak(from progress: UserProgress, now: Date = .now) -> UserProgress {
        var next = progress
        let calendar = Calendar.current

        guard let lastDate = progress.lastStudyDate else {
            next.currentStreak = 1
            next.longestStreak = max(next.longestStreak, 1)
            next.lastStudyDate = now
            return next
        }

        if calendar.isDate(lastDate, inSameDayAs: now) {
            return progress
        }

        let dayDifference = calendar.dateComponents([.day], from: calendar.startOfDay(for: lastDate), to: calendar.startOfDay(for: now)).day ?? 0
        next.currentStreak = dayDifference == 1 ? progress.currentStreak + 1 : 1
        next.longestStreak = max(next.longestStreak, next.currentStreak)
        next.lastStudyDate = now
        return next
    }
}
