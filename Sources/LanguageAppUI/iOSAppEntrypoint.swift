#if canImport(SwiftUI)
import SwiftUI

public struct FluentSprintRootApp: App {
    public init() {}

    public var body: some Scene {
        WindowGroup {
            HomeView()
        }
    }
}
#endif
