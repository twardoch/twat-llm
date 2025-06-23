#!/usr/bin/env python3
"""twat_llm:

Created by Adam Twardoch
"""

from __future__ import annotations

import logging
import os
from typing import Any, Literal, Union

import httpx
from pydantic import BaseModel, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

from .mallmo import ask  # Import from local mallmo module

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- Pydantic Models for Configuration ---
class ApiKeySettings(BaseSettings):
    """Manages API keys from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    proxycurl_api_key: str | None = Field(None, env="PROXYCURL_API_KEY")
    search_api_key: str | None = Field(None, env="SEARCH_API_KEY") # For chosen search provider


class PersonEnrichmentParams(BaseModel):
    """Parameters for enriching a person's profile."""

    linkedin_profile_url: HttpUrl | None = None
    email: str | None = None
    name: str | None = None
    # Add other relevant identifiers as needed, e.g., company, location
    company_name: str | None = None
    location: str | None = None


class WebSearchParams(BaseModel):
    """Parameters for performing a web search."""

    query: str = Field(..., description="The search query.")


class ActionConfig(BaseModel):
    """Defines an action to be performed and its parameters."""

    action_type: Literal["enrich_person", "search_web"] = Field(
        ..., description="The type of action to perform."
    )
    parameters: Union[PersonEnrichmentParams, WebSearchParams] = Field(
        ..., description="Parameters specific to the action."
    )
    api_keys: ApiKeySettings = Field(default_factory=ApiKeySettings)


def process_data(config: ActionConfig, *, debug: bool = False) -> dict[str, Any]:
    """Process the input data according to the provided action configuration.

    Args:
        config: The Pydantic model containing action type, parameters, and API keys.
        debug: Enable debug mode.

    Returns:
        Processed data as a dictionary.

    Raises:
        ValueError: If configuration is invalid or action type is unsupported.
        NotImplementedError: If the specified action is not yet implemented.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug(f"Debug mode enabled. Received config: {config.model_dump_json(indent=2)}")

    # API keys can be accessed via config.api_keys.proxycurl_api_key, etc.
    # These will be loaded from environment variables if available.

    if config.action_type == "enrich_person":
        if not isinstance(config.parameters, PersonEnrichmentParams):
            msg = "Invalid parameters for 'enrich_person' action."
            raise ValueError(msg)

        params: PersonEnrichmentParams = config.parameters
        api_key = config.api_keys.proxycurl_api_key

        if not api_key:
            msg = "PROXYCURL_API_KEY is required for person enrichment but not found."
            logger.error(msg)
            raise ValueError(msg)

        if not params.linkedin_profile_url:
            # TODO: Implement lookup by name/email if URL is not provided
            # For MVP, require LinkedIn URL.
            msg = "LinkedIn profile URL is required for person enrichment in this MVP version."
            logger.error(msg)
            raise ValueError(msg)

        headers = {"Authorization": f"Bearer {api_key}"}
        # Proxycurl Person Profile Endpoint
        # See: https://nubela.co/proxycurl/docs#people-api-person-profile-endpoint
        proxycurl_endpoint_url = "https://nubela.co/proxycurl/api/linkedin/person-profile"

        api_params = {
            "url": str(params.linkedin_profile_url),
            # Add other Proxycurl parameters as needed, e.g.:
            # 'fallback_to_cache': 'on-error',
            # 'use_cache': 'if-present',
            # 'skills': 'include',
            # 'inferred_salary': 'include',
            # 'personal_email': 'include',
            # 'personal_contact_number': 'include',
            # 'twitter_profile_id': 'include',
            # 'facebook_profile_id': 'include',
            # 'github_profile_id': 'include',
            # 'extra': 'include',
        }

        logger.info(f"Contacting Proxycurl API for LinkedIn URL: {params.linkedin_profile_url}")
        try:
            with httpx.Client() as client:
                response = client.get(proxycurl_endpoint_url, headers=headers, params=api_params, timeout=30.0)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            profile_data = response.json()

            # Summarize with mallmo.ask
            # Construct a prompt for summarization
            # Ensure profile_data is converted to a string, perhaps JSON string
            import json
            profile_json_str = json.dumps(profile_data, indent=2)
            summary_prompt = (
                "Based on the following JSON data of a person's profile, "
                "provide a concise summary (2-3 sentences) highlighting their current role, key skills, and experience. "
                "The summary should be suitable for understanding how to improve communication with them."
                f"\n\nProfile Data:\n{profile_json_str}"
            )

            logger.info("Sending profile data to LLM for summarization.")
            summary = ask(prompt=summary_prompt) # Uses default model in mallmo

            return {
                "status": "success",
                "action": "enrich_person",
                "linkedin_url": str(params.linkedin_profile_url),
                "raw_profile_data": profile_data, # Consider if returning full raw data is always desired
                "summary": summary,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Proxycurl API request failed: {e!s} - Response: {e.response.text}")
            # Potentially return error details or raise a custom app exception
            raise ValueError(f"Failed to retrieve data from Proxycurl: {e!s}") from e
        except httpx.RequestError as e:
            logger.error(f"Proxycurl API request failed: {e!s}")
            raise ValueError(f"Failed to connect to Proxycurl: {e!s}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred during person enrichment: {e!s}")
            raise ValueError(f"An unexpected error occurred: {e!s}") from e

    elif config.action_type == "search_web":
        if not isinstance(config.parameters, WebSearchParams):
            msg = "Invalid parameters for 'search_web' action."
            raise ValueError(msg)

        params: WebSearchParams = config.parameters
        api_key = config.api_keys.search_api_key # Using the generic name from ApiKeySettings

        if not api_key:
            msg = "SEARCH_API_KEY is required for web search but not found."
            logger.error(msg)
            raise ValueError(msg)

        # Using Brave Search API as an example
        # Endpoint: https://api.search.brave.com/res/v1/web/search
        # Requires header: X-Subscription-Token
        brave_search_api_url = "https://api.search.brave.com/res/v1/web/search"
        headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}
        api_params = {"q": params.query} # Brave uses 'q' for query

        logger.info(f"Contacting Brave Search API for query: {params.query}")
        try:
            with httpx.Client() as client:
                response = client.get(brave_search_api_url, headers=headers, params=api_params, timeout=20.0)
                response.raise_for_status()

            search_results = response.json() # Structure depends on Brave API (likely a list of results)

            # Create a string representation of search results for the LLM
            # This might involve picking top N results and formatting them.
            # For simplicity, just use the raw JSON string of all results for now.
            # A more sophisticated approach would extract titles, snippets, URLs.
            # Example:
            # formatted_results = ""
            # if "web" in search_results and "results" in search_results["web"]:
            #     for i, result in enumerate(search_results["web"]["results"][:5]): # Top 5
            #         formatted_results += f"Result {i+1}:\nTitle: {result.get('title')}\nSnippet: {result.get('description')}\nURL: {result.get('url')}\n\n"
            # else:
            #     formatted_results = "No detailed web results found."

            import json
            results_json_str = json.dumps(search_results, indent=2)

            summary_prompt = (
                "Based on the following web search results, provide a concise answer or summary "
                f"for the query: '{params.query}'. Focus on the most relevant information."
                f"\n\nSearch Results (JSON):\n{results_json_str}"
            )

            logger.info("Sending search results to LLM for summarization.")
            summary = ask(prompt=summary_prompt)

            return {
                "status": "success",
                "action": "search_web",
                "query": params.query,
                "raw_search_results": search_results, # Consider if returning all raw results is always desired
                "summary": summary,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Brave Search API request failed: {e!s} - Response: {e.response.text}")
            raise ValueError(f"Failed to retrieve data from Search API: {e!s}") from e
        except httpx.RequestError as e:
            logger.error(f"Brave Search API request failed: {e!s}")
            raise ValueError(f"Failed to connect to Search API: {e!s}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred during web search: {e!s}")
            raise ValueError(f"An unexpected error occurred: {e!s}") from e

    else:
        msg = f"Unsupported action type: {config.action_type}"
        raise ValueError(msg)

    # Dummy result for now
    # result: dict[str, Any] = {"status": "processing_started", "details": config.model_dump()}
    # return result


def main() -> None:
    """Main entry point for demonstrating twat_llm."""
    logger.info("Starting twat_llm demonstration...")

    # Attempt to load API keys from environment (or .env file if present)
    # For demonstration, we'll create configs. In real use, these might come from user input or another system.

    # Example 1: Enrich Person
    logger.info("\n--- Example: Person Enrichment ---")
    try:
        enrich_config = ActionConfig(
            action_type="enrich_person",
            parameters=PersonEnrichmentParams(
                linkedin_profile_url="http://linkedin.com/in/johndoe",  # type: ignore[arg-type]
                name="John Doe",
                email="john.doe@example.com"
            )
        )
        logger.info(f"Attempting Person Enrichment with config: {enrich_config.model_dump_json(indent=2)}")
        enrich_result = process_data(enrich_config, debug=True)
        logger.info(f"Person Enrichment Result: {enrich_result}")
    except ValueError as e:
        logger.warning(f"Person Enrichment failed (e.g., missing API key or bad input): {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during person enrichment demo: {e!s}")

    # Example 2: Web Search
    logger.info("\n--- Example: Web Search ---")
    try:
        search_config = ActionConfig(
            action_type="search_web",
            parameters=WebSearchParams(query="latest advancements in large language models")
        )
        logger.info(f"Attempting Web Search with config: {search_config.model_dump_json(indent=2)}")
        search_result = process_data(search_config, debug=True)
        logger.info(f"Web Search Result: {search_result}")
    except ValueError as e:
        logger.warning(f"Web Search failed (e.g., missing API key or bad input): {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during web search demo: {e!s}")

    logger.info("\nTwat_llm demonstration finished.")

    # Illustrate API key loading (optional, for clarity)
    loaded_api_keys = ApiKeySettings()
    if loaded_api_keys.proxycurl_api_key:
        logger.info("Proxycurl API key found (from env or .env).")
    else:
        logger.warning(
            "Proxycurl API key not found. Set PROXYCURL_API_KEY environment variable or add to .env file."
        )
    if loaded_api_keys.search_api_key:
        logger.info("Search API key found (from env or .env).")
    else:
        logger.warning(
            "Search API key not found. Set SEARCH_API_KEY environment variable or add to .env file."
        )

    # Example of how to handle missing data error from original process_data
    # try:
    #     process_data([], config=None) # This call is no longer valid with new ActionConfig
    # except ValueError as e:
    #    logger.warning(f"Caught expected ValueError for empty data (old API): {e}")

    # Note: The original `process_data` took a `data: list[Any]` argument.
    # This has been removed in the new Pydantic-based `ActionConfig` approach,
    # as parameters are now part of the config. If `data` is still needed,
    # it should be incorporated into the Pydantic models. For now, it's omitted.

    except Exception as e: # General catch for main, though specific examples have their own
        logger.exception(f"A general error occurred in main: {e!s}")
        raise


if __name__ == "__main__":
    main()
