# twat-llm

**twat-llm** is a Python library designed to simplify interactions with various Large Language Models (LLMs) and external data services. It provides a unified interface for tasks like data enrichment (e.g., fetching professional profiles) and web searching, augmented by LLM-powered summarization and processing. The library also includes robust utilities for handling media, chaining prompts, and batch processing LLM requests.

## Features

-   **Modern Python Development**: Built with Python 3.10+, using modern tooling like Hatch for project management and `pyproject.toml` for PEP 621 compliance.
-   **LLM Abstraction**: Easily interact with different LLMs through a consistent API (powered by the `llm` library).
-   **Data Enrichment**:
    -   Fetch and summarize professional profiles using services like Proxycurl.
    -   Perform web searches using services like Brave Search API and summarize results.
-   **Media Handling**: Utilities for processing images and extracting frames from videos for multimodal LLM inputs.
-   **Flexible Prompting**: Supports direct prompting, chained prompts for complex workflows, and batch processing for efficiency.
-   **Configurable Actions**: Use Pydantic models for clear and validated action configurations.
-   **Extensive Quality Assurance**: Includes a comprehensive test suite (pytest), linting (Ruff), and static type checking (MyPy).
-   **CI/CD Ready**: GitHub Actions for automated testing, building, and releasing.
-   **Semantic Versioning**: Versioning managed by `hatch-vcs` based on Git tags.

## Rationale

The primary goal of `twat-llm` is to provide a streamlined and robust toolkit for developers looking to integrate LLM capabilities with external data sources. Many applications require fetching data from APIs (like social media enrichment or web search) and then using LLMs to process, summarize, or derive insights from that data. `twat-llm` aims to:

-   Reduce boilerplate code for common LLM interaction patterns.
-   Offer a flexible way to define and execute data processing actions involving LLMs.
-   Provide helpful utilities for tasks often associated with LLM applications, such as media handling.
-   Encourage best practices in terms of code quality, testing, and dependency management.

## Installation

You can install `twat-llm` using pip:

```bash
pip install twat-llm
```

This will install the core package and its runtime dependencies.

### Extras

The package defines optional dependencies for development and testing:

-   `dev`: Includes tools like `ruff`, `mypy`, and `pre-commit` for development.
-   `test`: Includes `pytest`, `pytest-cov`, etc., for running tests.

To install with these extras:
```bash
pip install "twat-llm[dev,test]"
```
Or for all extras:
```bash
pip install "twat-llm[all]"
```

### API Keys

Some functionalities, like person enrichment (Proxycurl) and web search (e.g., Brave Search), require API keys. These are managed via environment variables. You can set them directly in your environment or place them in a `.env` file in your project root:

```env
# .env file example
PROXYCURL_API_KEY="your_proxycurl_api_key"
SEARCH_API_KEY="your_search_api_key"
# Add other API keys as needed by the llm library (e.g., OPENAI_API_KEY)
```

The library uses `pydantic-settings` to load these variables.

## Usage

The library offers two main ways to interact with LLMs and data services:
1.  High-level `process_data` function for predefined actions.
2.  Granular functions from the `mallmo` module for direct LLM calls, chaining, and batching.

### Using `process_data`

The `process_data` function uses an `ActionConfig` model to define what operation to perform.

```python
from twat_llm import process_data, ActionConfig, PersonEnrichmentParams, WebSearchParams

# Example 1: Enrich Person profile (requires PROXYCURL_API_KEY)
enrich_config = ActionConfig(
    action_type="enrich_person",
    parameters=PersonEnrichmentParams(
        linkedin_profile_url="https://www.linkedin.com/in/exampleprofile",
        name="John Doe", # Optional, can be used if URL is unknown (future enhancement)
        email="john.doe@example.com" # Optional
    )
)
try:
    enriched_data = process_data(enrich_config, debug=True)
    print("Enriched Person Data:", enriched_data)
except ValueError as e:
    print(f"Error enriching person: {e}")

# Example 2: Search Web (requires SEARCH_API_KEY for Brave Search, or configure other provider)
search_config = ActionConfig(
    action_type="search_web",
    parameters=WebSearchParams(query="latest advancements in AI")
)
try:
    search_summary = process_data(search_config, debug=True)
    print("Web Search Summary:", search_summary)
except ValueError as e:
    print(f"Error searching web: {e}")

```

### Using `mallmo` module directly

The `twat_llm.mallmo` module provides more direct control over LLM interactions.

```python
from pathlib import Path
from twat_llm import mallmo

# Simple prompt to an LLM (uses default models if not specified)
try:
    response = mallmo.ask("What is the capital of France?")
    print(f"LLM Response: {response}")
except mallmo.LLMError as e:
    print(f"Error with LLM: {e}")

# Prompt with input data
data_to_summarize = "Python is a versatile and widely-used programming language..."
summary_prompt = "Summarize the following text in one sentence: $input"
try:
    summary = mallmo.ask(prompt=summary_prompt, data=data_to_summarize)
    print(f"Summary: {summary}")
except mallmo.LLMError as e:
    print(f"Error summarizing: {e}")

# Prompt with media (ensure you have an image file 'example.jpg')
# Create a dummy image for the example if you don't have one
try:
    from PIL import Image
    dummy_image = Image.new('RGB', (60, 30), color = 'red')
    dummy_image.save("dummy_image.jpg")

    media_response = mallmo.ask(
        prompt="What is in this image?",
        media_paths=[Path("dummy_image.jpg")]
    )
    print(f"Media Response: {media_response}")
except mallmo.LLMError as e:
    print(f"Error with media prompt: {e}")
except FileNotFoundError:
    print("Dummy image not found. Please create 'dummy_image.jpg' to run this example.")


# Chaining prompts and functions
def uppercase_text(text: str) -> str:
    return text.upper()

try:
    chain_steps = [
        "What is the capital of France?",
        uppercase_text,
        "Translate the following to Spanish: $input"
    ]
    final_result = mallmo.ask_chain("Initial data (not used by first prompt)", chain_steps)
    print(f"Chained result: {final_result}")
except mallmo.LLMError as e:
    print(f"Error in chain: {e}")


# Batch processing prompts (media not supported in batch via this simple function)
prompts_list = [
    "What is 2+2?",
    "What is the color of the sky?"
]
try:
    batch_responses = mallmo.ask_batch(prompts_list)
    for i, res in enumerate(batch_responses):
        print(f"Batch Response {i+1}: {res}")
except mallmo.BatchProcessingError as e:
    print(f"Error in batch processing: {e}")

```

## Development

This project uses [Hatch](https://hatch.pypa.io/) for environment and project management, and [uv](https://github.com/astral-sh/uv) for faster package installation and resolution within Hatch.

### Setup Development Environment

1.  **Install Hatch and uv**:
    If you don't have them, install Hatch and uv. Pipx is recommended for CLI tools:
    ```bash
    pipx install hatch
    pipx install uv
    ```
    Alternatively, use pip:
    ```bash
    pip install --user hatch uv
    ```

2.  **Activate Hatch Environment**:
    Navigate to the project root directory and run:
    ```bash
    hatch shell
    ```
    This will create a virtual environment (using `uv` if available) and install all dependencies, including development tools.

### Running Quality Checks and Tests

The following commands can be run from within the activated Hatch environment (after `hatch shell`) or by prefixing with `hatch run <env>:<script_name>` (e.g., `hatch run default:test`).

-   **Run tests**:
    ```bash
    pytest
    # or
    hatch run test
    ```

-   **Run tests with coverage**:
    ```bash
    hatch run test:test-cov
    ```

-   **Run linters and formatters (Ruff)**:
    ```bash
    hatch run lint:style  # Runs ruff check and ruff format
    # For auto-fixing:
    hatch run lint:fmt
    ```

-   **Run type checking (MyPy)**:
    ```bash
    hatch run lint:typing
    ```

-   **Run all linters and type checker**:
    ```bash
    hatch run lint:all
    ```

-   **`cleanup.py` Script**:
    A utility script `cleanup.py` is provided for various maintenance tasks. It's configured to run with `uv`.
    ```bash
    ./cleanup.py status  # Check current status and run checks
    ./cleanup.py update  # Run checks and commit changes
    ```
    Make sure it's executable (`chmod +x cleanup.py`).

### Pre-commit Hooks

This project uses pre-commit hooks to automatically check and format code before commits. To install:
```bash
pip install pre-commit
pre-commit install
```
This will run Ruff and MyPy on staged files during `git commit`.

## Codebase Structure

-   **`src/twat_llm/`**: Main source code directory.
    -   `__init__.py`: Makes the directory a package and exports `__version__`.
    -   `twat_llm.py`: Contains the high-level `process_data` function and Pydantic models for action configurations (`ActionConfig`, `PersonEnrichmentParams`, `WebSearchParams`, `ApiKeySettings`). This is the primary entry point for structured LLM-driven data processing tasks.
    -   `mallmo.py`: Provides core LLM interaction utilities like `ask` (for single prompts with media support), `ask_chain` (for sequential processing steps), and `ask_batch` (for parallel prompt execution). It also includes helper functions for media processing.
    -   `__version__.py`: Automatically generated by `hatch-vcs` during the build process to store the package version.
-   **`tests/`**: Contains unit and integration tests.
    -   `test_twat_llm.py`: Tests for `twat_llm.py`.
    -   `test_mallmo.py`: Tests for `mallmo.py`.
-   **`examples/`**: Contains example scripts demonstrating usage of the library.
-   **`docs/`**: Documentation files.
    -   `research/`: Contains research notes and API explorations (may be integrated into more formal docs later).
-   **`pyproject.toml`**: Defines project metadata, dependencies, and tool configurations (Hatch, Ruff, MyPy, Pytest).
-   **`.pre-commit-config.yaml`**: Configuration for pre-commit hooks.
-   **`LICENSE`**: MIT License file.
-   **`README.md`**: This file.
-   **`cleanup.py`**: Utility script for development tasks.

## Contribution Guidelines

Contributions are welcome! Please follow these guidelines:

1.  **Fork and Clone**: Fork the repository and clone it locally.
2.  **Create a Branch**: Create a new branch for your feature or bug fix: `git checkout -b feature/your-feature-name` or `fix/your-bug-fix`.
3.  **Develop**: Make your changes. Ensure your code adheres to the existing style (Ruff will help enforce this). Add type hints for new functions and classes.
4.  **Test**:
    *   Write new tests for any new functionality.
    *   Ensure all tests pass by running `hatch run test:test-cov`. Aim for high test coverage.
5.  **Lint and Format**:
    *   Run `hatch run lint:all` to check for linting issues and type errors. Fix any reported problems.
6.  **Commit**: Use clear and descriptive commit messages. Consider using [Conventional Commits](https://www.conventionalcommits.org/) if you are familiar with it.
7.  **Push**: Push your changes to your fork: `git push origin feature/your-feature-name`.
8.  **Create a Pull Request**: Open a pull request against the `main` branch of the original repository. Provide a clear description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
