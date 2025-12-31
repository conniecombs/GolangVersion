# Changelog

All notable changes to Connie's Uploader Ultimate will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.0] - 2025-01-01

### Added
- ViperGirls forum integration with auto-posting functionality
- Thread management system for saving and organizing forum threads
- Auto-post queue with proper ordering and cooldown management
- Viper Tools dialog for managing forum credentials and threads
- Post holding pen for batch-ordered forum posting
- Separate batches option for individual file uploads
- Central history folder in user directory (`~/.conniesuploader/history/`)
- Improved gallery management across all services
- Template editor with live preview functionality
- Context menu integration for Windows Explorer
- Execution log window for debugging

### Changed
- Refactored service settings into modular `ServiceSettingsView` class
- Improved error handling and recovery mechanisms
- Enhanced UI responsiveness during uploads
- Better progress tracking with per-file and batch-level status
- Optimized thumbnail generation with thread pool executor
- Updated Go backend with worker pool implementation (8 concurrent workers)

### Fixed
- Fixed icon loading issues on different platforms
- Improved sidecar process management and cleanup
- Fixed race conditions in upload progress updates
- Better handling of failed uploads and retry logic
- Fixed vipr.im gallery refresh and selection
- Resolved issues with pixhost gallery finalization

## [3.4.0] - 2024-12-15

### Added
- ImageBam support with session-based authentication
- Gallery creation for ImageBam service
- Improved credential management with secure keyring storage
- Dark/Light/System appearance mode toggle

### Changed
- Migrated to CustomTkinter for modern UI appearance
- Improved template system with more customization options
- Enhanced drag-and-drop functionality for files and groups

### Fixed
- Fixed turboimagehost endpoint detection
- Improved vipr.im upload reliability
- Better error messages for failed uploads

## [3.3.0] - 2024-11-20

### Added
- Turboimagehost support
- Batch upload progress bar
- Overall upload progress tracking
- Retry failed uploads functionality
- Cover image count configuration per service

### Changed
- Improved multi-threading with configurable thread limits
- Better file organization with group-based uploads
- Enhanced output formatting with templates

### Fixed
- Fixed memory leaks in thumbnail generation
- Improved cleanup of temporary files
- Better handling of special characters in filenames

## [3.2.0] - 2024-10-30

### Added
- vipr.im support with folder organization
- Gallery manager dialog
- Auto-gallery creation per folder option
- Template manager for BBCode/HTML output
- Links-only output file option

### Changed
- Refactored upload manager for better separation of concerns
- Improved API error handling and retry logic
- Better progress feedback during uploads

### Fixed
- Fixed pixhost gallery hash handling
- Improved imx.to API error messages
- Better handling of network timeouts

## [3.1.0] - 2024-09-15

### Added
- Pixhost.to support with gallery management
- Thumbnail size configuration per service
- Content rating options for services
- Auto-copy to clipboard feature
- Drag-and-drop for file reordering

### Changed
- Redesigned settings panel with service-specific tabs
- Improved credentials dialog organization
- Better file validation and error messages

### Fixed
- Fixed issues with large file uploads
- Improved stability with concurrent uploads
- Better handling of API rate limits

## [3.0.0] - 2024-08-01

### Added
- Complete rewrite with Go backend for high-performance uploads
- Worker pool architecture for efficient concurrent processing
- JSON-RPC communication between Python UI and Go backend
- Support for multiple image hosting services
- Drag-and-drop interface
- Real-time progress tracking
- Image preview thumbnails

### Changed
- Migrated from pure Python to hybrid Python/Go architecture
- New modern UI with CustomTkinter
- Improved upload speed with concurrent processing
- Better memory management

### Removed
- Legacy threading implementation
- Old UI framework dependencies

## [2.0.0] - 2024-06-15

### Added
- GUI implementation with Tkinter
- Multi-threaded uploads
- Basic progress tracking
- Settings persistence

## [1.0.0] - 2024-05-01

### Added
- Initial release
- Command-line interface
- Basic imx.to upload support
- API key authentication

---

## Release Types

- **Major version (X.0.0)**: Incompatible API changes or major architectural changes
- **Minor version (0.X.0)**: New features in a backward-compatible manner
- **Patch version (0.0.X)**: Backward-compatible bug fixes

[3.5.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v3.5.0
[3.4.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v3.4.0
[3.3.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v3.3.0
[3.2.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v3.2.0
[3.1.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v3.1.0
[3.0.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v3.0.0
[2.0.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v2.0.0
[1.0.0]: https://github.com/conniecombs/GolangVersion/releases/tag/v1.0.0
