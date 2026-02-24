import Foundation
import LanguageCore

#if canImport(SwiftUI)
import SwiftUI

@MainActor
public final class AppViewModel: ObservableObject {
    @Published public private(set) var progress: UserProgress
    @Published public private(set) var todayPlan: [Lesson]

    private let repository: ProgressStoring
    private let learningPath = LearningPathService()

    public init(repository: ProgressStoring = ProgressRepository(), catalog: [Lesson] = SampleData.catalog) {
        self.repository = repository
        let loaded = (try? repository.load()) ?? UserProgress(selectedLanguage: "Spanish", targetLevel: .b2)
        self.progress = loaded
        self.todayPlan = learningPath.recommendedLessons(from: catalog, progress: loaded, dailyTimeBudgetMinutes: 20)
    }

    public func complete(_ lesson: Lesson, now: Date = .now) {
        progress.completedLessonIDs.insert(lesson.id)
        progress = learningPath.updatedStreak(from: progress, now: now)
        try? repository.save(progress)
        todayPlan.removeAll { $0.id == lesson.id }
    }
}

public struct HomeView: View {
    @StateObject private var viewModel = AppViewModel()

    public init() {}

    public var body: some View {
        NavigationStack {
            List {
                Section("Streak") {
                    HStack {
                        Text("Current")
                        Spacer()
                        Text("\(viewModel.progress.currentStreak) days")
                    }
                    HStack {
                        Text("Best")
                        Spacer()
                        Text("\(viewModel.progress.longestStreak) days")
                    }
                }

                Section("Today's Micro-Lessons") {
                    ForEach(viewModel.todayPlan) { lesson in
                        Button {
                            viewModel.complete(lesson)
                        } label: {
                            VStack(alignment: .leading) {
                                Text(lesson.title).font(.headline)
                                Text("\(lesson.estimatedMinutes) minutes").font(.subheadline)
                            }
                        }
                    }
                }
            }
            .navigationTitle("FluentSprint")
        }
    }
}

public enum SampleData {
    public static let catalog: [Lesson] = [
        Lesson(title: "Airport Survival Phrases", level: .a1, estimatedMinutes: 5, tags: ["travel"]),
        Lesson(title: "Restaurant Confidence", level: .a2, estimatedMinutes: 8, tags: ["food"]),
        Lesson(title: "Past Tense Sprint", level: .b1, estimatedMinutes: 10, tags: ["grammar"]),
        Lesson(title: "Workplace Small Talk", level: .b2, estimatedMinutes: 12, tags: ["career"])
    ]
}

#else
public enum AppViewModelUnavailable {
    public static let reason = "SwiftUI is unavailable on this platform."
}
#endif
