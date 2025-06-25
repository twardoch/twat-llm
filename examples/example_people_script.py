"""
Example script to demonstrate person enrichment using twat_llm.

This script shows how to use the `process_data` function with `ActionConfig`
and `PersonEnrichmentParams` to fetch and summarize a person's professional profile.

Requirements:
- Ensure the `twat-llm` package is installed.
- Set the PROXYCURL_API_KEY environment variable. You can get an API key from
  https://nubela.co/proxycurl. For example, create a .env file in your project root:
  PROXYCURL_API_KEY="your_actual_api_key"
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
    # It's good practice to handle potential ImportError if the package structure changes
    # or if it's run from a place where the package isn't correctly installed/visible.
    from twat_llm import (
        ActionConfig,
        PersonEnrichmentParams,
        process_data,
    )
except ImportError:
    logger.error(
        "Failed to import twat_llm components. "
        "Ensure 'twat-llm' is installed and accessible in your Python environment."
    )
    raise


def enrich_person_example(linkedin_url: str):
    """
    Demonstrates enriching a person's profile using their LinkedIn URL.

    Args:
        linkedin_url: The LinkedIn profile URL to enrich.
    """
    logger.info(f"Attempting to enrich profile for LinkedIn URL: {linkedin_url}")

    # 1. Create PersonEnrichmentParams
    # For MVP, we primarily use linkedin_profile_url.
    # Name and email are optional and might be used for future lookup strategies.
    person_params = PersonEnrichmentParams(
        linkedin_profile_url=linkedin_url,
        # name="John Doe", # Optional
        # email="john.doe@example.com" # Optional
    )

    # 2. Create ActionConfig
    # The ApiKeySettings will be automatically populated from environment variables
    # (e.g., PROXYCURL_API_KEY from .env file or environment).
    enrich_action_config = ActionConfig(
        action_type="enrich_person",
        parameters=person_params
    )

    # 3. Call process_data
    try:
        logger.info(f"Sending request with config: {enrich_action_config.model_dump_json(indent=2, exclude_none=True)}")
        result = process_data(enrich_action_config, debug=True) # Enable debug for more verbose logging

        logger.info("\n--- Person Enrichment Result ---")
        if result.get("status") == "success":
            print(f"LinkedIn URL: {result.get('linkedin_url')}") # noqa: T201
            print(f"\nLLM Summary:\n{result.get('summary')}") # noqa: T201
            # print(f"\nRaw Profile Data (excerpt):\n{str(result.get('raw_profile_data', {}))[:500]}...") # Optional: print some raw data
        else:
            print(f"Enrichment failed. Details: {result.get('details', 'No details provided.')}") # noqa: T201

    except ValueError as ve:
        logger.error(f"Configuration or API error during person enrichment: {ve}")
        print(f"Error: {ve}") # noqa: T201
        print("Please ensure PROXYCURL_API_KEY is set correctly in your environment or .env file.") # noqa: T201
    except Exception as e:
        logger.exception(f"An unexpected error occurred during person enrichment: {e}")
        print(f"An unexpected error occurred: {e}") # noqa: T201


if __name__ == "__main__":
    # Replace with a public LinkedIn profile URL for testing
    # Note: Scraping LinkedIn profiles, even via an API like Proxycurl,
    # should be done in accordance with LinkedIn's ToS and Proxycurl's terms.
    # Using a well-known public figure or a test account is advisable.
    example_linkedin_url = "https://www.linkedin.com/in/satyanadella/" # Example public profile

    if "your_actual_api_key" in open(__file__).read(): # Basic check
        print( # noqa: T201
            "Reminder: Replace placeholder API key information in environment variables or .env file."
        )

    enrich_person_example(example_linkedin_url)

    # You can try another example if you have another URL
    # example_linkedin_url_2 = "https://linkedin.com/in/williamhgates"
    # if example_linkedin_url_2:
    #     print("\n")
    #     enrich_person_example(example_linkedin_url_2)

    print("\nPerson enrichment example finished.") # noqa: T201
    print("Ensure PROXYCURL_API_KEY is set in your environment or .env file.") # noqa: T201
    print("Ensure your `llm` library is configured with models for summarization.") # noqa: T201

# To run this example:
# 1. Make sure twat-llm is installed (`pip install .` or `pip install twat-llm`)
# 2. Create a .env file in the same directory as this script (or project root)
#    with your PROXYCURL_API_KEY:
#    PROXYCURL_API_KEY="your_key_here"
# 3. Run `python examples/example_people_script.py`
```
