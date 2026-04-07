# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2024-12-01

### Added

- New **Metadata Settings** tab for configuring persistent metadata fields:
  - Author / Artist name (EXIF Artist, XMP Creator)
  - Copyright notice (EXIF Copyright)
  - Keywords / Tags (XMP Subject, semicolon-separated)
  - Star Rating (XMP Rating, 0-5)
  - Custom Comment (EXIF UserComment)
- Modern dark theme with consistent styling across all widgets
- Tooltips on all metadata fields explaining what EXIF/XMP tags they map to
- Auto-save for all metadata fields

### Changed

- Rebranded from "MSFS GeoShot" to "MSFS MetaShot" to reflect enhanced metadata capabilities
- Updated for Microsoft Flight Simulator 2024 compatibility
- Updated all dependencies to their latest versions:
  - Python ^3.10, PyQt5 ^5.15.11, Pillow ^11.1.0, psutil ^6.1.0, geopy ^2.4.1, and more
- Enlarged default window size for better usability
- Source metadata now reads "MSFS 2024" instead of "MSFS"
- Improved UI description text

### Fixed

- Fixed bug in `_tear_down_input_widget_connections` where `start_to_tray` used `connect` instead of `disconnect`
- Fixed bug in `MetadataService.write_data` where `capture_time` was compared by value instead of attribute name

## [1.0.0-beta.2] - 2021-09-26

### Fixed

- Fixed an issue that would cause the initial settings to be set to the wrong values (thanks to vbazillio for the heads-up!)
- Fixed an issue that would prevent MSFS GeoShot from capturing screenshots when MSFS was minimized

### Changed

- Screenshots taken in windowed mode now exclude the window border and window decorations

### Added

- Added a link to the flightsim.to listing to the UI
- Added feedback dialog

## [1.0.0-beta.1] - 2021-09-22

Initial release

[Unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v1.0.0-beta.1...HEAD
[1.0.0-beta.1]: https://github.com/olivierlacan/keep-a-changelog/releases/tag/v1.0.0-beta.1