// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "LanguageApp",
    platforms: [
        .iOS(.v17),
        .macOS(.v14)
    ],
    products: [
        .library(name: "LanguageCore", targets: ["LanguageCore"]),
        .library(name: "LanguageAppUI", targets: ["LanguageAppUI"])
    ],
    targets: [
        .target(
            name: "LanguageCore",
            path: "Sources/LanguageCore"
        ),
        .target(
            name: "LanguageAppUI",
            dependencies: ["LanguageCore"],
            path: "Sources/LanguageAppUI"
        ),
        .testTarget(
            name: "LanguageCoreTests",
            dependencies: ["LanguageCore"],
            path: "Tests/LanguageCoreTests"
        )
    ]
)
