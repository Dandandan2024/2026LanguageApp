# FluentSprint (2026LanguageApp)

FluentSprint is a modern language-learning iOS app foundation designed for rapid daily fluency gains through:
- Personalized micro-lessons.
- Streak-based habit loops.
- Spaced repetition review.
- Performance-first, privacy-friendly local persistence.

## What is production-ready in this repo

- **Core domain logic** in `LanguageCore` with test coverage.
- **SwiftUI UI module** in `LanguageAppUI` for home dashboard + daily plan.
- **Deterministic learning services** for recommendations and review scheduling.
- **CI-ready Swift test workflow** via GitHub Actions.

## Architecture

- `Sources/LanguageCore`
  - Models (`Lesson`, `UserProgress`, `VocabularyCard`).
  - Services (`LearningPathService`, `SpacedRepetitionScheduler`).
  - Storage (`ProgressRepository`).
- `Sources/LanguageAppUI`
  - `HomeView` and `AppViewModel` (SwiftUI app experience).
- `Tests/LanguageCoreTests`
  - Unit tests for recommendation engine, streak logic, review scheduling, and persistence.

## Local development

```bash
swift test
```

## Next milestones to become App Store-leading

1. Add speech recognition scoring + pronunciation feedback.
2. Integrate adaptive placement test and AI conversation simulator.
3. Add analytics, experiments, and subscription/paywall strategy.
4. Harden offline sync + conflict resolution with CloudKit.
5. Complete legal/compliance pack (privacy nutrition labels, COPPA/GDPR flows).
