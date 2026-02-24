import Foundation

public protocol ProgressStoring {
    func load() throws -> UserProgress
    func save(_ progress: UserProgress) throws
}

public struct ProgressRepository: ProgressStoring {
    private let defaults: UserDefaults
    private let key = "language.progress.v1"

    public init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    public func load() throws -> UserProgress {
        guard let data = defaults.data(forKey: key) else {
            return UserProgress(selectedLanguage: "Spanish", targetLevel: .b2)
        }

        return try JSONDecoder().decode(UserProgress.self, from: data)
    }

    public func save(_ progress: UserProgress) throws {
        let data = try JSONEncoder().encode(progress)
        defaults.set(data, forKey: key)
    }
}
