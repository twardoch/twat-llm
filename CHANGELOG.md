# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - YYYY-MM-DD

### Added
- This `CHANGELOG.md` file to track changes.
- `PLAN.md` outlining the streamlining strategy for v1.0 MVP.
- `TODO.md` providing a task list for the streamlining effort.

### Changed
- Condensed `docs/research/people-api.md` to a summary focused on Proxycurl integration for MVP.
- Condensed `docs/research/web-search-api.md` to a summary focused on Brave Search API (as an example) integration for MVP.
- Rewrote `examples/example_people_script.py` to use `process_data`, `ActionConfig`, and `PersonEnrichmentParams` from `twat_llm`, and to guide on API key environment setup.
- Rewrote `examples/example_serp_script.py` to use `process_data`, `ActionConfig`, and `WebSearchParams` from `twat_llm`, and to guide on API key environment setup.
- Updated `examples/funchain_example.py` to use the correct import path for `ask_chain`, added a `main()` function, logging, and print statements for clarity.
- Moved demonstration logic from `main()` in `src/twat_llm/twat_llm.py` to a new example script `examples/run_action_config_example.py`.
- Updated `src/twat_llm/__init__.py` to export key public interfaces from `twat_llm.py` and `mallmo.py`.
- Streamlined dependencies in `pyproject.toml` for MVP by removing `opencv-python-headless`.
- Adjusted `src/twat_llm/mallmo.py` to remove video processing capabilities (dependent on `opencv-python-headless`), focusing only on image media types for MVP.

### Removed
- Removed detailed internal review files from `docs/research/`:
    - `review-copilot.md`
    - `review-cursor.md`
    - `review-o3.md`
    - `review-trae.md`
- Removed `docs/research/people-api-tldr.md` to reduce redundancy and focus documentation on implemented MVP features.

### Fixed
-   *(Placeholder for bug fixes during streamlining)*

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
- Added `llm_plugins.py` for checking installed LLM plugins (Note: This file is `examples/check_llm_plugins.py` in current structure)
- Created `funchain.py` as a simple example of chain functionality (Note: This file is `examples/funchain_example.py` in current structure)
- Basic project structure with Python package setup

### Changed

- Moved `twat_llm.py` to `src/twat_llm/` directory
- Enhanced code quality with type hints and modern Python features
- Improved error handling and logging

### Fixed

- Added missing newline at end of files
- Updated `.gitignore` to exclude `_private` directory

---
*Note: The initial content for v0.0.1 is based on the existing `LOG.md`. `LOG.md` might be superseded by this `CHANGELOG.md` or integrated into it.*
