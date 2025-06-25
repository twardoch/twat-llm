# TODO List for twat-llm v1.0 MVP Streamlining

This list summarizes the actionable tasks derived from `PLAN.md`.

## Phase 1: Documentation & Non-Core File Cleanup

-   [ ] **`docs/research/` Cleanup:**
    -   [ ] Condense `people-api.md`: Retain a summary of chosen APIs (Proxycurl) and key considerations. Archive or remove detailed comparisons.
    -   [ ] Condense `web-search-api.md`: Retain a summary of chosen APIs (Brave Search) and key considerations. Archive or remove detailed comparisons.
    -   [ ] Review `people-api-tldr.md`: Integrate relevant parts into README or condensed `people-api.md`; remove if redundant.
    -   [ ] Remove internal review files: `review-copilot.md`, `review-cursor.md`, `review-o3.md`, `review-trae.md`.
-   [ ] **`.specstory/` & `.cursor/rules/`:** Confirm they are handled by `.gitignore` or are development-only aids; no direct code changes to library.
-   [ ] **Generated Files (`CLEANUP.txt`, `REPO_CONTENT.txt`):** Verify they are in `.gitignore` and `cleanup.py` manages them appropriately.

## Phase 2: Example Scripts & Utility Scripts Review

-   [ ] **`examples/` Review:**
    -   [ ] `check_llm_plugins.py`: Confirm it's useful and functional.
    -   [ ] `example_people_script.py`: Simplify, ensure clear demonstration of `process_data` with `PersonEnrichmentParams`, and guide on API key handling.
    -   [ ] `example_serp_script.py`: Simplify, ensure clear demonstration of `process_data` with `WebSearchParams`, and guide on API key handling.
    -   [ ] `funchain_example.py`: Review for clarity and relevance to `ask_chain` as an MVP feature.
-   [ ] **`cleanup.py` Review:**
    -   [ ] Verify all its functions (`status`, `venv`, `install`, `update`, `push`, `repomix`) are working and streamlined.
    -   [ ] Consider if `repomix` call needs to be conditional or a separate command. (For now, assume current behavior is acceptable).

## Phase 3: Core Code Refinement (`src/`)

-   [ ] **`src/twat_llm/twat_llm.py` Review:**
    -   [ ] `process_data` function: Confirm robustness for MVP. Defer major refactoring of common logic unless critical.
    -   [ ] Ensure summarization prompts are adequate for MVP.
    -   [ ] Verify error handling (`httpx.HTTPStatusError`, `httpx.RequestError`).
    -   [ ] `ApiKeySettings`: Confirm correct loading for all services.
    -   [ ] `ActionConfig` and related Pydantic models: Confirm `model_validator` and discriminator logic work as expected.
    -   [ ] `main()` function: Move demonstration logic to a new example script in `examples/`.
-   [ ] **`src/twat_llm/mallmo.py` Review:**
    -   [ ] Core Functions (`ask`, `_try_model`, `_prepare_media`): Ensure robustness and error handling.
    -   [ ] Media preparation (`_prepare_media`, `_resize_image`, `_extract_middle_frame`): Verify efficiency and correctness.
    -   [ ] Advanced Features (`ask_chain`, `ask_batch`): Confirm they are needed for MVP and function correctly. (Current assumption: retain).
    -   [ ] CLI in `mallmo.py`: Confirm it's functional.
-   [ ] **`src/twat_llm/__init__.py` Review:**
    -   [ ] Update `__all__` to export the public API for the library (e.g., `ActionConfig`, `process_data`, `ask`).

## Phase 4: Dependencies & Configuration Review

-   [ ] **`pyproject.toml` Review:**
    -   [ ] `opencv-python-headless`: Confirm if video processing is critical for MVP. If not, consider making it optional or deferring. (Current assumption: retain).
    -   [ ] Review other dependency versions.
-   [ ] **`.gitignore` Review:**
    -   [ ] Confirm all necessary generated files and directories are ignored.

## Phase 5: Final Review, Testing & Changelog

-   [ ] Run all quality checks: `ruff`, `mypy`.
-   [ ] Run all tests: `pytest`. Ensure full coverage for MVP features.
-   [ ] Manually review all changes.
-   [ ] Update `PLAN.md` and `TODO.md` to reflect completed work.
-   [ ] Finalize `CHANGELOG.md`.

## Phase 6: Submission

-   [ ] Commit all changes with a descriptive message.
-   [ ] Use an appropriate branch name for submission.
