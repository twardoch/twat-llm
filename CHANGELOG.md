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

### Added

- `DEFAULT_MAX_PROCESSES` constant in `mallmo.py` for configurable batch parallelism
- `docs/index.md` — user-facing documentation explaining what an LLM is and how to use the library
- `docs/api.md` — full public API reference for `ask`, `ask_chain`, `ask_batch`, text adapters, and `process_data`

### Changed

- `cli()` in `mallmo.py`: now prints responses and error messages to stdout/stderr (previously returned silently); passes `data=None` explicitly to `ask()`
- `WebSearchParams.query` field now enforces `min_length=1` (empty queries raise `ValidationError`)
- Test suite: fixed 6 benchmark tests using `side_effect` instead of `return_value=iter(...)` to prevent iterator exhaustion across benchmark rounds
- Test suite: fixed env-var isolation in `test_api_key_settings_no_env` and `test_api_key_settings_validation` using `monkeypatch`
- Test suite: fixed integration CLI tests that assumed `cwd="/root/repo"` (Docker-only path)

[unreleased]: https://github.com/twardoch/twat-llm/compare/v0.0.1...HEAD
[v0.0.1]: https://github.com/twardoch/twat-llm/releases/tag/v0.0.1
