# `twat-llm`: Advanced LLM Integration for Python Applications

**`twat-llm`** is a powerful Python library designed to streamline the integration of Large Language Models (LLMs) with external data sources and services. It empowers Python developers to easily build sophisticated applications that leverage the analytical capabilities of LLMs for tasks such as data enrichment, web content analysis, and complex, chained operations. As part of the [twat](https://pypi.org/project/twat/) collection of tools, `twat-llm` adheres to high standards of modern Python development, offering a robust and flexible solution.

## Who is `twat-llm` for?

This library is aimed at Python developers who need to:

*   Interact with various LLMs through a unified and simplified interface.
*   Enrich data by fetching and processing information from external APIs (e.g., professional profiles from Proxycurl, web search results from Brave Search).
*   Implement complex workflows involving multiple LLM calls or a sequence of data processing steps.
*   Handle media inputs (images) for multimodal LLMs.
*   Ensure their applications are built with well-tested, type-checked, and maintainable code.

## Why is `twat-llm` useful?

`twat-llm` significantly reduces boilerplate and complexity when working with LLMs and external data by providing:

*   **Simplified LLM Interaction:** An easy-to-use API (`mallmo.ask`) for single LLM prompts, supporting model fallbacks and retries.
*   **Structured Data Processing:** A high-level interface (`process_data` with `ActionConfig`) for predefined tasks like person data enrichment and web search summarization.
*   **External Service Integration:** Built-in support for services like Proxycurl (LinkedIn data) and Brave Search API, with LLM-powered summarization of their outputs.
*   **Flexible Prompting & Chaining:** Support for direct prompting, incorporating external data into prompts, and chaining multiple LLM calls or Python functions for complex workflows (`mallmo.ask_chain`).
*   **Efficient Batch Processing:** Capability to process multiple prompts in parallel for improved performance (`mallmo.ask_batch`).
*   **Media Handling:** Utilities for processing and attaching images to LLM prompts.
*   **Robust Development Practices:** Built with modern Python (3.10+), using Hatch for project management, Ruff for linting, MyPy for type checking, and a comprehensive test suite with Pytest.

## Installation

You can install `twat-llm` directly from PyPI using pip:

```bash
pip install twat-llm
```

This command installs the core package and its essential runtime dependencies.

### Optional Dependencies (Extras)

`twat-llm` defines optional dependencies for development and testing. You can install these extras as needed:

*   **`dev`**: Includes tools for development such as `ruff` (linter/formatter), `mypy` (static type checker), and `pre-commit`.
*   **`test`**: Includes `pytest` and related plugins for running the test suite.
*   **`all`**: Installs all optional dependencies.

To install with specific extras:

```bash
pip install "twat-llm[dev,test]"
```

Or to install everything including all optional features and development tools:

```bash
pip install "twat-llm[all]"
```

### API Key Configuration

To use functionalities that interact with external services, you'll need to configure API keys. `twat-llm` uses `pydantic-settings` to load these from environment variables or a `.env` file located in your project's root directory.

**Required API Keys for certain features:**

*   **Proxycurl (Person Enrichment):**
    *   Set `PROXYCURL_API_KEY="your_proxycurl_api_key"`
    *   Needed for the `enrich_person` action.
*   **Brave Search (Web Search):**
    *   Set `SEARCH_API_KEY="your_brave_search_api_key"`
    *   Needed for the `search_web` action using the default Brave Search provider.

**General LLM Provider API Keys:**

The underlying `llm` library (by Simon Willison) is used for LLM interactions. You need to configure it with API keys for your chosen LLM providers (e.g., OpenAI, Anthropic, OpenRouter). Refer to the [`llm` library documentation on configuring keys](https://llm.datasette.io/en/stable/setup.html#configuring-keys) for detailed instructions. Common environment variables include:

*   `OPENAI_API_KEY`
*   `ANTHROPIC_API_KEY`
*   etc.

**Example `.env` file:**

Create a file named `.env` in your project root:

```env
# For twat-llm specific services
PROXYCURL_API_KEY="your_proxycurl_api_key_here"
SEARCH_API_KEY="your_brave_search_api_key_here"

# For the LLM library (examples)
OPENAI_API_KEY="your_openai_api_key_here"
# ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

## How to Use

`twat-llm` offers multiple ways to interact with its features, catering to both quick command-line tasks and more complex programmatic integrations.

### Command-Line Interface (CLI)

The `mallmo` module provides a CLI for direct LLM interactions, powered by `python-fire`. You can access it by running `python -m twat_llm.mallmo`.

**Basic Prompts:**

Send a simple prompt to the default LLM:
```bash
python -m twat_llm.mallmo --prompt "What is the capital of Canada?"
```

Specify a model to use (ensure it's supported by your `llm` library configuration):
```bash
python -m twat_llm.mallmo --prompt "Translate 'hello' to Spanish" --model gpt-4o-mini
```

**Prompts with Media:**

Ask a question about an image:
```bash
python -m twat_llm.mallmo --prompt "What is in this image?" --media path/to/your/image.jpg
```
*(Supported image formats include JPG, PNG, GIF, BMP, WEBP, TIFF.)*

**Batch Processing:**

Process multiple prompts from a file (one prompt per line):
```bash
# prompts.txt:
# What is 2+2?
# Summarize the concept of photosynthesis.

python -m twat_llm.mallmo --batch_prompts_file prompts.txt
```

Save batch output to a file:
```bash
python -m twat_llm.mallmo --batch_prompts_file prompts.txt --output_file responses.txt
```

Specify number of parallel processes for batch execution:
```bash
python -m twat_llm.mallmo --batch_prompts_file prompts.txt --processes 4
```

### Programmatic Usage

For integration into your Python applications, `twat-llm` provides two main approaches:

1.  **High-Level `process_data` Function:** For predefined, structured actions like data enrichment and web searching.
2.  **Direct `mallmo` Module Functions:** For more granular control over LLM calls, chaining, and batching.

#### 1. Using `process_data` for Structured Actions

The `process_data` function (from `twat_llm.twat_llm`) uses an `ActionConfig` model to define operations. This is ideal for standardized tasks.

**Example: Enrich Person Profile (Proxycurl)**

Requires `PROXYCURL_API_KEY`.
```python
from twat_llm import process_data, ActionConfig, PersonEnrichmentParams

# Define parameters for person enrichment
enrich_params = PersonEnrichmentParams(
    linkedin_profile_url="https://www.linkedin.com/in/exampleprofile"
)

# Create the action configuration
enrich_config = ActionConfig(
    action_type="enrich_person",
    parameters=enrich_params
)

try:
    # Set debug=True for more verbose logging
    enriched_data = process_data(enrich_config, debug=True)
    print("Enriched Person Summary:", enriched_data.get("summary"))
    # print("Full enriched data:", enriched_data)
except ValueError as e:
    print(f"Error enriching person: {e}")
```

**Example: Search Web and Summarize (Brave Search)**

Requires `SEARCH_API_KEY`.
```python
from twat_llm import process_data, ActionConfig, WebSearchParams

# Define parameters for web search
search_params = WebSearchParams(query="latest trends in renewable energy")

# Create the action configuration
search_config = ActionConfig(
    action_type="search_web",
    parameters=search_params
)

try:
    search_summary = process_data(search_config, debug=True)
    print("Web Search Summary:", search_summary.get("summary"))
    # print("Full search data:", search_summary)
except ValueError as e:
    print(f"Error searching web: {e}")
```

#### 2. Using the `mallmo` Module Directly

The `twat_llm.mallmo` module offers finer control.

**Basic Prompting with `mallmo.ask()`**

```python
from twat_llm import mallmo
from pathlib import Path

try:
    # Simple prompt (uses default LLM models)
    response = mallmo.ask("What is the airspeed velocity of an unladen swallow?")
    print(f"LLM Response: {response}")

    # Prompt with input data
    text_to_summarize = "The quick brown fox jumps over the lazy dog. This sentence contains all letters of the alphabet."
    summary = mallmo.ask(
        prompt="Summarize this text in one short sentence: $input",
        data=text_to_summarize
    )
    print(f"Summary: {summary}")

    # Prompt with an image (ensure 'dummy_image.jpg' exists or change path)
    # from PIL import Image
    # Image.new('RGB', (60, 30), color = 'red').save("dummy_image.jpg") # Create dummy if needed
    image_response = mallmo.ask(
        prompt="Describe this image.",
        media_paths=[Path("dummy_image.jpg")] # Ensure this file exists for the example
    )
    print(f"Image Description: {image_response}")

except mallmo.LLMError as e:
    print(f"An LLM error occurred: {e}")
except mallmo.MediaProcessingError as e:
    print(f"A media processing error occurred: {e}")
```

**Chaining Prompts and Functions with `mallmo.ask_chain()`**

`ask_chain` processes a sequence of steps. Each step can be an LLM prompt (string) or a Python callable. The output of one step becomes the input (`$input` or first argument) to the next.

```python
from twat_llm import mallmo

def add_exclamation(text: str) -> str:
    return text + "!"

def to_uppercase(text: str) -> str:
    return text.upper()

try:
    chain_steps = [
        "Tell me a short joke about computers.", # Step 1: LLM prompt
        add_exclamation,                       # Step 2: Python function
        to_uppercase,                          # Step 3: Python function
        "Translate the following to French: $input" # Step 4: LLM prompt
    ]

    # Initial data for the chain (can be empty if first step doesn't need it)
    initial_data = ""
    final_result = mallmo.ask_chain(initial_data, chain_steps)
    print(f"Chained Result (in French): {final_result}")

except mallmo.LLMError as e:
    print(f"Error in chain: {e}")
```

**Batch Processing Prompts with `mallmo.ask_batch()`**

Process multiple prompts in parallel. Media attachments are not supported in this batch function for simplicity.

```python
from twat_llm import mallmo

prompts_list = [
    "What is the primary function of a CPU?",
    "Name three benefits of using Python.",
    "Define 'artificial intelligence' in simple terms."
]

try:
    # Optionally specify model_ids or num_processes
    batch_responses = mallmo.ask_batch(prompts_list)
    for i, res in enumerate(batch_responses):
        print(f"Response {i+1}: {res}")
except mallmo.BatchProcessingError as e:
    print(f"Error in batch processing: {e}")
```

## How the Code Works: Technical Deep Dive

This section provides a more detailed look into the architecture and core components of `twat-llm`.

### Core Modules and Components

The library's functionality is primarily organized into two main Python modules within the `src/twat_llm` directory:

1.  **`twat_llm.py` (High-Level Orchestration)**
    *   **Purpose:** Provides the `process_data` function, which acts as the main entry point for structured, predefined data processing actions (e.g., "enrich_person", "search_web").
    *   **`ActionConfig`:** A Pydantic `BaseModel` that defines the structure for an action request. It includes:
        *   `action_type`: A literal string specifying the action (e.g., `"enrich_person"`).
        *   `parameters`: A discriminated union (`AnyParams`) of Pydantic models specific to each action type (e.g., `PersonEnrichmentParams`, `WebSearchParams`). This ensures that parameters are validated against the correct schema for the specified action.
        *   `api_keys`: An instance of `ApiKeySettings`.
    *   **Parameter Models (e.g., `PersonEnrichmentParams`, `WebSearchParams`):** These Pydantic models define the expected inputs for each specific action, enabling automatic validation and clear error messages.
    *   **`ApiKeySettings`:** A Pydantic `BaseSettings` model responsible for loading API keys (e.g., `PROXYCURL_API_KEY`, `SEARCH_API_KEY`) from environment variables or a `.env` file.
    *   **Workflow:**
        1.  `process_data` receives an `ActionConfig`.
        2.  It validates the `action_type` and routes to a corresponding internal handler function (e.g., `_handle_enrich_person`, `_handle_search_web`).
        3.  Handler functions use `httpx` to make synchronous API calls to external services (like Proxycurl or Brave Search).
        4.  The JSON data received from these services is then passed to `mallmo.ask()` along with a specific prompt to an LLM for summarization or analysis.
        5.  The final result, including raw data and the LLM-generated summary, is returned as a dictionary.
    *   **Error Handling:** Uses custom `ValueError` exceptions for configuration issues or API failures, often wrapping `httpx.HTTPStatusError` or `httpx.RequestError`.

2.  **`mallmo.py` (Core LLM Interaction Layer)**
    *   **Purpose:** Contains the fundamental logic for interacting with LLMs, handling media, chaining operations, and batch processing. It's designed to be more granular and flexible than `twat_llm.py`.
    *   **`ask(prompt, data, model_ids, media_paths)` Function:**
        *   The primary function for sending a single prompt to an LLM.
        *   **Prompt Formatting:** If `data` is provided, it's incorporated into the `prompt` string (replaces `$input` placeholder or appends).
        *   **Media Processing:**
            *   If `media_paths` are provided, `_prepare_media` is called for each path.
            *   `_prepare_media` uses Pillow (`PIL`) to open images, and `_resize_image` to resize them (maintaining aspect ratio, converting to RGB, and saving as JPEG bytes) to a manageable size (default max 512x512). Video processing was previously included but has been removed for MVP streamlining.
            *   Processed media are converted to `llm.Attachment` objects.
        *   **Model Fallback & Retry:**
            *   It iterates through a list of model IDs (`model_ids`), (defaults to `DEFAULT_FALLBACK_MODELS` like "gpt-4o-mini", "openrouter/google/gemini-flash-1.5", etc.).
            *   For each model, `_try_model` is called. This function uses `tenacity` for automatic retries with exponential backoff in case of `ModelInvocationError`.
            *   If a model doesn't support multimodal input but media is provided, it's skipped.
            *   The first successful model response is returned.
        *   **LLM Interaction:** Uses the `llm` library by Simon Willison to interact with the actual LLM APIs.
    *   **`ask_chain(data, steps)` Function:**
        *   Processes an iterable of `steps`. Each step can be:
            *   A string (which is treated as an LLM prompt and passed to `ask()`).
            *   A Python callable (function/method).
            *   A tuple of `(processor, kwargs_dict)` for more complex calls.
        *   The output of one step is passed as input to the subsequent step (either as the `$input` variable in a prompt string or as the first argument to a callable).
    *   **`ask_batch(prompts, model_ids, num_processes)` Function:**
        *   Processes a sequence of `prompts` in parallel.
        *   Uses `concurrent.futures.ProcessPoolExecutor` to distribute the `_process_single_prompt_for_batch` calls (which internally uses `ask`) across multiple CPU cores.
        *   Media attachments are not supported in this batch function to simplify parallel execution.
    *   **Error Handling:** Defines and uses custom exceptions:
        *   `LLMError` (base class)
        *   `MediaProcessingError`
        *   `ModelInvocationError`
        *   `BatchProcessingError`
    *   **CLI:** Includes a `cli` function that uses `python-fire` to expose `ask` and `ask_batch` functionalities via the command line (`python -m twat_llm.mallmo ...`).

### Key Libraries and Their Roles

*   **`llm` (by Simon Willison):** The backbone for LLM communication. It provides a unified API to various LLM providers, manages model discovery, and handles API key configurations for these providers. `twat-llm` leverages it for the actual prompt execution.
*   **`Pydantic` & `pydantic-settings`:** Used extensively for data validation, defining clear schemas for configurations (`ActionConfig`, parameter models), and loading settings/API keys from environment variables or `.env` files.
*   **`httpx`:** A modern, asynchronous-capable HTTP client (though used synchronously in `twat_llm.py`). It's employed for making requests to external APIs like Proxycurl and Brave Search.
*   **`Pillow` (PIL Fork):** Used in `mallmo.py` for image manipulation tasks, specifically opening, resizing, and converting images before they are sent to multimodal LLMs.
*   **`tenacity`:** Provides robust retry mechanisms for operations that might fail transiently, primarily used in `_try_model` within `mallmo.py` when attempting LLM calls.
*   **`fire`:** Enables the quick creation of a command-line interface for the `mallmo.py` module, making its functions directly accessible from the shell.
*   **`Hatch` & `hatchling`:** The build system and project management tool used for dependency management, environment setup, running scripts (tests, linters), and packaging the library.

### Configuration Overview

*   **`pyproject.toml`:** The central configuration file for the project. It defines:
    *   Project metadata (name, version, author, license, etc.).
    *   Core dependencies and optional extras (`[project.dependencies]`, `[project.optional-dependencies]`).
    *   Build system configuration (`[build-system]`).
    *   Hatch environment and script configurations (`[tool.hatch.envs]`).
    *   Tool configurations for Ruff (linter), MyPy (type checker), Pytest, and Coverage.
*   **API Keys:** As detailed in the Installation section, API keys for external services (`PROXYCURL_API_KEY`, `SEARCH_API_KEY`) and LLM providers (via the `llm` library) are managed through environment variables, often facilitated by a `.env` file and loaded by `pydantic-settings`.

This structure allows `twat-llm` to offer both easy-to-use high-level abstractions for common tasks and more powerful, granular control for custom LLM workflows.

## Development & Contribution Guidelines

We welcome contributions to `twat-llm`! To ensure a smooth development process and maintain code quality, please follow these guidelines.

### Setting Up Your Development Environment

This project uses [Hatch](https://hatch.pypa.io/) for project management, dependency management, and running development tasks. [uv](https://github.com/astral-sh/uv) is often used by Hatch under the hood for faster environment setup if available.

1.  **Install Hatch and uv (Recommended):**
    If you don't have them, install Hatch (and optionally uv, though Hatch may manage it). Using `pipx` is recommended for CLI tools:
    ```bash
    pipx install hatch
    pipx install uv # Optional, but recommended for speed with Hatch
    ```
    Alternatively, use pip:
    ```bash
    pip install --user hatch uv
    ```

2.  **Activate the Hatch Environment:**
    Navigate to the project's root directory and run:
    ```bash
    hatch shell
    ```
    This command creates a virtual environment (or reuses an existing one managed by Hatch) and installs all project dependencies, including development tools specified in `pyproject.toml`.

### Code Style and Quality

Consistent code style and high quality are maintained using the following tools:

*   **Linting and Formatting (Ruff):**
    [Ruff](https://beta.ruff.rs/docs/) is used as an extremely fast Python linter and formatter.
    *   Check for style issues: `hatch run lint:style`
    *   Format code automatically: `hatch run lint:fmt` (runs `ruff format` and `ruff check --fix`)
    *   Run all lint checks: `hatch run lint:all` (includes style and type checking)
    Configuration for Ruff can be found in `pyproject.toml` under `[tool.ruff]`.

*   **Type Checking (MyPy):**
    [MyPy](http://mypy-lang.org/) is used for static type checking to catch type errors before runtime.
    *   Run type checks: `hatch run lint:typing`
    *   MyPy configuration is in `pyproject.toml` under `[tool.mypy]`.

*   **Pre-commit Hooks:**
    This project uses pre-commit hooks to automatically run linters and type checkers on staged files before they are committed. This helps catch issues early.
    1.  Install pre-commit: `pip install pre-commit`
    2.  Install the hooks: `pre-commit install`
    Now, Ruff and MyPy will run automatically when you `git commit`. Configuration is in `.pre-commit-config.yaml`.

### Testing

A comprehensive test suite is crucial for ensuring reliability.

*   **Running Tests (Pytest):**
    [Pytest](https://docs.pytest.org/) is used as the testing framework.
    *   Run all tests: `hatch run test` (or simply `pytest` within the Hatch shell)
    *   Run tests with coverage report: `hatch run test:test-cov`
    *   Test files are located in the `tests/` directory and should follow the `test_*.py` naming convention.
*   **Writing Tests:**
    *   New features or bug fixes **must** include corresponding tests.
    *   Aim for high test coverage. Check the coverage report generated by `hatch run test:test-cov`.

### Contribution Workflow

1.  **Fork the Repository:** Create a fork of the `twat-llm` repository on GitHub.
2.  **Clone Your Fork:** Clone your forked repository to your local machine.
    ```bash
    git clone https://github.com/YOUR_USERNAME/twat-llm.git
    cd twat-llm
    ```
3.  **Create a Branch:** Create a new branch for your feature or bug fix. Use a descriptive name (e.g., `feature/add-new-service` or `fix/resolve-api-error`).
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Develop:**
    *   Make your code changes.
    *   Ensure your code adheres to the project's style guidelines (Ruff will help).
    *   Add type hints for all new functions, methods, and classes.
5.  **Test:** Write new tests for your changes and ensure all tests pass (`hatch run test:test-cov`).
6.  **Lint and Type Check:** Run `hatch run lint:all` and fix any reported issues. Ensure pre-commit hooks also pass.
7.  **Commit Your Changes:** Use clear and descriptive commit messages. Consider following the [Conventional Commits](https://www.conventionalcommits.org/) specification.
    ```bash
    git add .
    git commit -m "feat: Add support for X service"
    ```
8.  **Push to Your Fork:** Push your changes to your forked repository.
    ```bash
    git push origin feature/your-feature-name
    ```
9.  **Create a Pull Request (PR):** Open a pull request from your branch in your fork to the `main` branch of the original `twardoch/twat-llm` repository.
    *   Provide a clear title and a detailed description of your changes in the PR.
    *   Link any relevant issues.

### Versioning

This project uses `hatch-vcs` for versioning, which means the package version is dynamically determined from Git tags. Releases should follow [Semantic Versioning (SemVer)](https://semver.org/).

### `AGENTS.MD` / `CLAUDE.MD`

Currently, no project-specific `AGENTS.MD` or `CLAUDE.MD` file with overriding instructions has been identified. Please adhere to the general guidelines outlined in this README. If such a file is introduced later, its instructions will take precedence for the scope it defines.
