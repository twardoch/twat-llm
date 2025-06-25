"""
Example script to demonstrate using ActionConfig with process_data from twat_llm.

This script shows how to:
- Configure person enrichment and web search actions.
- Execute these actions using `process_data`.
- Handle API keys via environment variables (loaded by ApiKeySettings).

Requirements:
- Ensure the `twat-llm` package is installed.
- For person enrichment: Set PROXYCURL_API_KEY environment variable.
- For web search: Set SEARCH_API_KEY (e.g., for Brave Search) environment variable.
  (Create a .env file in your project root or set them in your shell)
  Example .env:
  PROXYCURL_API_KEY="your_proxycurl_key"
  SEARCH_API_KEY="your_search_key"
- Ensure LLM models are configured for the `llm` library for summarization.
"""
from __future__ import annotations

import logging

# Configure basic logging for the example
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

try:
    from twat_llm import (
        ActionConfig,
        ApiKeySettings, # To illustrate API key loading messages
        PersonEnrichmentParams,
        WebSearchParams,
        process_data,
    )
except ImportError:
    logger.error(
        "Failed to import twat_llm components. "
        "Ensure 'twat-llm' is installed and accessible in your Python environment."
    )
    raise


def main_demonstration():
    """Demonstrates person enrichment and web search actions."""
    logger.info("Starting twat_llm demonstration using ActionConfig...")

    # --- Example 1: Enrich Person ---
    logger.info("\n--- Example: Person Enrichment ---")
    try:
        # For this example, using a public profile.
        # Replace with a relevant LinkedIn URL for your tests.
        enrich_params = PersonEnrichmentParams(
            linkedin_profile_url="https://www.linkedin.com/in/satyanadella/", # Example
            name="Satya Nadella", # Optional, for context
            # email="satya.nadella@example.com" # Optional
        )
        enrich_config = ActionConfig(
            action_type="enrich_person",
            parameters=enrich_params
        )
        logger.info(f"Attempting Person Enrichment with config: {enrich_config.model_dump_json(indent=2, exclude_none=True)}")
        enrich_result = process_data(enrich_config, debug=True)
        logger.info(f"Person Enrichment Result: {enrich_result}")
        if enrich_result.get("status") == "success":
            print("\nPerson Enrichment Succeeded:") # noqa: T201
            print(f"  Summary: {enrich_result.get('summary')}") # noqa: T201
        else:
            print(f"\nPerson Enrichment Failed: {enrich_result.get('details')}") # noqa: T201

    except ValueError as e:
        logger.warning(f"Person Enrichment failed (e.g., missing API key or bad input): {e}")
        print(f"\nPerson Enrichment Error: {e}") # noqa: T201
    except Exception as e:
        logger.exception(f"An unexpected error occurred during person enrichment demo: {e!s}")
        print(f"\nUnexpected Person Enrichment Error: {e}") # noqa: T201

    # --- Example 2: Web Search ---
    logger.info("\n--- Example: Web Search ---")
    try:
        search_params = WebSearchParams(
            query="latest news on generative AI models"
        )
        search_config = ActionConfig(
            action_type="search_web",
            parameters=search_params
        )
        logger.info(f"Attempting Web Search with config: {search_config.model_dump_json(indent=2, exclude_none=True)}")
        search_result = process_data(search_config, debug=True)
        logger.info(f"Web Search Result: {search_result}")
        if search_result.get("status") == "success":
            print("\nWeb Search Succeeded:") # noqa: T201
            print(f"  Query: {search_result.get('query')}") # noqa: T201
            print(f"  Summary: {search_result.get('summary')}") # noqa: T201
        else:
            print(f"\nWeb Search Failed: {search_result.get('details')}") # noqa: T201

    except ValueError as e:
        logger.warning(f"Web Search failed (e.g., missing API key or bad input): {e}")
        print(f"\nWeb Search Error: {e}") # noqa: T201
    except Exception as e:
        logger.exception(f"An unexpected error occurred during web search demo: {e!s}")
        print(f"\nUnexpected Web Search Error: {e}") # noqa: T201

    logger.info("\nTwat_llm ActionConfig demonstration finished.")

    # Illustrate API key loading messages (optional, for clarity)
    loaded_api_keys = ApiKeySettings()
    if loaded_api_keys.proxycurl_api_key:
        logger.info("Proxycurl API key was found by ApiKeySettings (from env or .env).")
    else:
        logger.warning(
            "Proxycurl API key was NOT found by ApiKeySettings. "
            "Set PROXYCURL_API_KEY environment variable or add to .env file for person enrichment."
        )
    if loaded_api_keys.search_api_key:
        logger.info("Search API key was found by ApiKeySettings (from env or .env).")
    else:
        logger.warning(
            "Search API key was NOT found by ApiKeySettings. "
            "Set SEARCH_API_KEY environment variable or add to .env file for web search."
        )

if __name__ == "__main__":
    main_demonstration()
    print( # noqa: T201
        "\nRun complete. Ensure necessary API keys (PROXYCURL_API_KEY, SEARCH_API_KEY) "
        "are set in your environment or a .env file."
    )
    print("Also ensure your `llm` library is configured with models for summarization.") # noqa: T201

# To run this example:
# 1. Make sure twat-llm is installed (`pip install .` or `pip install twat-llm`)
# 2. Create a .env file in the same directory as this script (or project root)
#    with your API keys:
#    PROXYCURL_API_KEY="your_proxycurl_key_here"
#    SEARCH_API_KEY="your_search_api_key_here" (e.g., Brave Search API token)
# 3. Run `python examples/run_action_config_example.py`
```
