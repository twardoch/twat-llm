"""
Example script to demonstrate web search using twat_llm.

This script shows how to use the `process_data` function with `ActionConfig`
and `WebSearchParams` to perform a web search and get an LLM-generated summary.

Requirements:
- Ensure the `twat-llm` package is installed.
- Set the SEARCH_API_KEY environment variable. The current `twat_llm.py` implementation
  is configured for the Brave Search API (https://brave.com/search/api/).
  You'll need a Brave Search API key (X-Subscription-Token).
  Create a .env file in your project root:
  SEARCH_API_KEY="your_brave_search_api_key"
- Ensure you have LLM models configured for the `llm` library, as `mallmo.ask`
  (used by `process_data`) will use them for summarization.
  See https://llm.datasette.io/en/stable/models/index.html for model setup.
"""
from __future__ import annotations

import logging

# Configure basic logging for the example
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from twat_llm import (
        ActionConfig,
        WebSearchParams,
        process_data,
    )
except ImportError:
    logger.error(
        "Failed to import twat_llm components. "
        "Ensure 'twat-llm' is installed and accessible in your Python environment."
    )
    raise


def web_search_example(query: str):
    """
    Demonstrates performing a web search and summarizing the results.

    Args:
        query: The search query string.
    """
    logger.info(f"Attempting web search for query: \"{query}\"")

    # 1. Create WebSearchParams
    search_params = WebSearchParams(query=query)

    # 2. Create ActionConfig
    # ApiKeySettings will be automatically populated from environment variables
    # (e.g., SEARCH_API_KEY for Brave Search from .env file or environment).
    search_action_config = ActionConfig(
        action_type="search_web",
        parameters=search_params
    )

    # 3. Call process_data
    try:
        logger.info(f"Sending request with config: {search_action_config.model_dump_json(indent=2, exclude_none=True)}")
        result = process_data(search_action_config, debug=True) # Enable debug for more verbose logging

        logger.info("\n--- Web Search Result ---")
        if result.get("status") == "success":
            print(f"Query: {result.get('query')}") # noqa: T201
            print(f"\nLLM Summary/Answer:\n{result.get('summary')}") # noqa: T201
            # You can also inspect raw search results if needed:
            # print(f"\nRaw Search Results (excerpt):\n{str(result.get('raw_search_results', {}))[:500]}...") # Optional
        else:
            print(f"Web search failed. Details: {result.get('details', 'No details provided.')}") # noqa: T201

    except ValueError as ve:
        logger.error(f"Configuration or API error during web search: {ve}")
        print(f"Error: {ve}") # noqa: T201
        print("Please ensure SEARCH_API_KEY (e.g., for Brave Search) is set correctly in your environment or .env file.") # noqa: T201
    except Exception as e:
        logger.exception(f"An unexpected error occurred during web search: {e}")
        print(f"An unexpected error occurred: {e}") # noqa: T201


if __name__ == "__main__":
    example_query = "latest advancements in large language models"

    if "your_brave_search_api_key" in open(__file__).read(): # Basic check
        print( # noqa: T201
            "Reminder: Replace placeholder API key information in environment variables or .env file."
        )

    web_search_example(example_query)

    # Example with a different query
    # example_query_2 = "What is the weather in London?"
    # if example_query_2:
    #     print("\n")
    #     web_search_example(example_query_2)

    print("\nWeb search example finished.") # noqa: T201
    print("Ensure SEARCH_API_KEY (e.g., for Brave Search) is set in your environment or .env file.") # noqa: T201
    print("Ensure your `llm` library is configured with models for summarization.") # noqa: T201

# To run this example:
# 1. Make sure twat-llm is installed (`pip install .` or `pip install twat-llm`)
# 2. Create a .env file in the same directory as this script (or project root)
#    with your SEARCH_API_KEY (e.g., Brave Search API token):
#    SEARCH_API_KEY="your_key_here"
# 3. Run `python examples/example_serp_script.py`
```
