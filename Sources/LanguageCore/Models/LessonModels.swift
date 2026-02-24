import Foundation

public struct Lesson: Identifiable, Codable, Hashable, Sendable {
    public let id: UUID
    public let title: String
    public let level: CEFRLevel
    public let estimatedMinutes: Int
    public let tags: [String]

    public init(id: UUID = UUID(), title: String, level: CEFRLevel, estimatedMinutes: Int, tags: [String]) {
        self.id = id
        self.title = title
        self.level = level
        self.estimatedMinutes = estimatedMinutes
        self.tags = tags
    }
}

public enum CEFRLevel: String, Codable, CaseIterable, Sendable {
    case a1, a2, b1, b2, c1, c2
}

public struct VocabularyCard: Identifiable, Codable, Hashable, Sendable {
    public let id: UUID
    public let prompt: String
    public let answer: String
    public let lessonID: UUID

    public init(id: UUID = UUID(), prompt: String, answer: String, lessonID: UUID) {
        self.id = id
        self.prompt = prompt
        self.answer = answer
        self.lessonID = lessonID
    }
}
