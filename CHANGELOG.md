# Changelog

All notable changes to SciTeX Writer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `scripts/init_project.sh` - Initialize project with required preprocessing artifacts (#12)
- `scripts/containers/` - Container definition directory with organized structure
  - `texlive.def` - Apptainer definition for TeX Live environment
  - `mermaid.def` - Apptainer definition for Mermaid diagram generation
  - `Dockerfile` - Docker configuration for TeX Live environment
- AI writing prompts in `ai/prompts/` for scientific manuscript assistance

### Fixed
- Working directory handling in compile scripts (#13)
  - Scripts now resolve project root from script location
  - Works correctly when invoked from any directory (MCP, CI/CD, IDEs)

### Changed
- Compile scripts now use absolute path resolution for better portability
- Shellcheck compliance improvements in compile scripts

## [2.0.0-rc3] - 2025-11-18

### Added
- AI prompts for scientific writing assistance
  - Abstract writing guidelines
  - Introduction writing guidelines
  - Methods writing guidelines
  - Discussion writing guidelines
  - General proofreading guidelines

## [2.0.0-rc2] - 2025-11-12

### Added
- Three-engine compilation system (Apptainer, Docker, Native)
- Auto-detection of available compilation engines
- Parallel asset processing for faster compilation

### Changed
- Improved compilation logging with stage timestamps
- Streamlined configuration loading

## [2.0.0-rc1] - 2025-11-08

### Added
- Complete LaTeX manuscript compilation system
- Automatic figure/table processing
- Bibliography merging from multiple sources
- Version tracking with diff generation
- Support for manuscript, supplementary, and revision documents

### Changed
- Restructured project for better modularity
- Separated configuration from scripts

[Unreleased]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.0.0-rc3...HEAD
[2.0.0-rc3]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.0.0-rc2...v2.0.0-rc3
[2.0.0-rc2]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.0.0-rc1...v2.0.0-rc2
[2.0.0-rc1]: https://github.com/ywatanabe1989/scitex-writer/releases/tag/v2.0.0-rc1
