---
this_file: LOG.md
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.0.1] - 2025-02-15

### Added

- Initial release of the project
- Created `mallmo.py` with LLM interaction functionality:
  - Core `ask()` function for LLM prompting with media support
  - `ask_batch()` for parallel processing of multiple prompts
  - `ask_chain()` for chaining multiple prompts or functions
  - Support for multiple fallback models
  - Media file processing (images and video frames)
  - CLI interface
- Added `llm_plugins.py` for checking installed LLM plugins
- Created `funchain.py` as a simple example of chain functionality
- Basic project structure with Python package setup

### Changed

- Moved `twat_llm.py` to `src/twat_llm/` directory
- Enhanced code quality with type hints and modern Python features
- Improved error handling and logging

### Fixed

- Added missing newline at end of files
- Updated `.gitignore` to exclude `_private` directory

## [Unreleased]

### To Do

- Implement core data processing logic in `twat_llm.py`
- Add comprehensive test coverage
- Enhance documentation with usage examples
- Consider adding more LLM providers and models

[unreleased]: https://github.com/twardoch/twat-llm/compare/v0.0.1...HEAD
[v0.0.1]: https://github.com/twardoch/twat-llm/releases/tag/v0.0.1 
