import Foundation

public struct UserProgress: Codable, Hashable, Sendable {
    public var selectedLanguage: String
    public var targetLevel: CEFRLevel
    public var currentStreak: Int
    public var longestStreak: Int
    public var lastStudyDate: Date?
    public var completedLessonIDs: Set<UUID>
    public var masteredCardIDs: Set<UUID>

    public init(
        selectedLanguage: String,
        targetLevel: CEFRLevel,
        currentStreak: Int = 0,
        longestStreak: Int = 0,
        lastStudyDate: Date? = nil,
        completedLessonIDs: Set<UUID> = [],
        masteredCardIDs: Set<UUID> = []
    ) {
        self.selectedLanguage = selectedLanguage
        self.targetLevel = targetLevel
        self.currentStreak = currentStreak
        self.longestStreak = longestStreak
        self.lastStudyDate = lastStudyDate
        self.completedLessonIDs = completedLessonIDs
        self.masteredCardIDs = masteredCardIDs
    }
}
