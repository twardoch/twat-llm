#!/usr/bin/env python3
"""twat_llm:

Created by Adam Twardoch
"""

from __future__ import annotations

import logging
import json  # Moved import json to top level
from typing import Any, Literal, Annotated  # Added Annotated

import httpx
from pydantic import BaseModel, Field, HttpUrl, model_validator  # Added model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from twat_llm.mallmo import ask  # Import from local mallmo module

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- Pydantic Models for Configuration ---
class ApiKeySettings(BaseSettings):
    """Manages API keys from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    proxycurl_api_key: str | None = Field(None, env="PROXYCURL_API_KEY")
    search_api_key: str | None = Field(
        None, env="SEARCH_API_KEY"
    )  # For chosen search provider


class PersonEnrichmentParams(BaseModel):
    """Parameters for enriching a person's profile."""

    action_type: Literal["enrich_person"] = "enrich_person"
    linkedin_profile_url: HttpUrl | None = None
    email: str | None = None
    name: str | None = None
    # Add other relevant identifiers as needed, e.g., company, location
    company_name: str | None = None
    location: str | None = None


class WebSearchParams(BaseModel):
    """Parameters for performing a web search."""

    action_type: Literal["search_web"] = "search_web"
    query: str = Field(..., description="The search query.")


AnyParams = Annotated[
    PersonEnrichmentParams | WebSearchParams, Field(discriminator="action_type")
]


class ActionConfig(BaseModel):
    """Defines an action to be performed and its parameters."""

    action_type: Literal["enrich_person", "search_web"] = Field(
        ..., description="The type of action to perform."
    )
    parameters: AnyParams
    api_keys: ApiKeySettings = Field(default_factory=ApiKeySettings)

    @model_validator(mode="before")
    @classmethod
    def _add_action_type_to_params(cls, values: Any) -> Any:
        if isinstance(values, dict):
            action_type = values.get("action_type")
            parameters = values.get("parameters")
            if (
                action_type
                and isinstance(parameters, dict)
                and "action_type" not in parameters
            ):
                # Create a new dict for parameters to avoid modifying the original
                # if it's shared or immutable, though Pydantic usually handles this.
                updated_parameters = parameters.copy()
                updated_parameters["action_type"] = action_type
                values["parameters"] = updated_parameters
        return values


def _handle_enrich_person(
    params: PersonEnrichmentParams, api_keys: ApiKeySettings
) -> dict[str, Any]:
    """Handles the person enrichment action."""
    api_key = api_keys.proxycurl_api_key
    if not api_key:
        msg = "PROXYCURL_API_KEY is required for person enrichment but not found."
        logger.error(msg)
        raise ValueError(msg)

    if not params.linkedin_profile_url:
        msg = "LinkedIn profile URL is required for person enrichment in this MVP version."
        logger.error(msg)
        raise ValueError(msg)

    headers = {"Authorization": f"Bearer {api_key}"}
    proxycurl_endpoint_url = "https://nubela.co/proxycurl/api/linkedin/person-profile"
    api_params = {"url": str(params.linkedin_profile_url)}

    logger.info(
        f"Contacting Proxycurl API for LinkedIn URL: {params.linkedin_profile_url}"
    )
    try:
        with httpx.Client() as client:
            response = client.get(
                proxycurl_endpoint_url, headers=headers, params=api_params, timeout=30.0
            )
            response.raise_for_status()
        profile_data = response.json()

        profile_json_str = json.dumps(profile_data, indent=2)
        summary_prompt = (
            "Based on the following JSON data of a person's profile, "
            "provide a concise summary (2-3 sentences) highlighting their current role, key skills, and experience. "
            "The summary should be suitable for understanding how to improve communication with them."
            f"\n\nProfile Data:\n{profile_json_str}"
        )
        logger.info("Sending profile data to LLM for summarization.")
        summary = ask(prompt=summary_prompt)

        return {
            "status": "success",
            "action": "enrich_person",
            "linkedin_url": str(params.linkedin_profile_url),
            "raw_profile_data": profile_data,
            "summary": summary,
        }
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Proxycurl API request failed: {e!s} - Response: {e.response.text}"
        )
        msg = f"Failed to retrieve data from Proxycurl: {e!s}"
        raise ValueError(msg) from e
    except httpx.RequestError as e:
        logger.error(f"Proxycurl API request failed: {e!s}")
        msg = f"Failed to connect to Proxycurl: {e!s}"
        raise ValueError(msg) from e
    except Exception as e:
        logger.exception(
            f"An unexpected error occurred during person enrichment: {e!s}"
        )
        msg = f"An unexpected error occurred: {e!s}"
        raise ValueError(msg) from e


def _handle_search_web(
    params: WebSearchParams, api_keys: ApiKeySettings
) -> dict[str, Any]:
    """Handles the web search action."""
    api_key = api_keys.search_api_key
    if not api_key:
        msg = "SEARCH_API_KEY is required for web search but not found."
        logger.error(msg)
        raise ValueError(msg)

    brave_search_api_url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": api_key, "Accept": "application/json"}
    api_params = {"q": params.query}

    logger.info(f"Contacting Brave Search API for query: {params.query}")
    try:
        with httpx.Client() as client:
            response = client.get(
                brave_search_api_url, headers=headers, params=api_params, timeout=20.0
            )
            response.raise_for_status()
        search_results = response.json()

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
            "raw_search_results": search_results,
            "summary": summary,
        }
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Brave Search API request failed: {e!s} - Response: {e.response.text}"
        )
        msg = f"Failed to retrieve data from Search API: {e!s}"
        raise ValueError(msg) from e
    except httpx.RequestError as e:
        logger.error(f"Brave Search API request failed: {e!s}")
        msg = f"Failed to connect to Search API: {e!s}"
        raise ValueError(msg) from e
    except Exception as e:
        logger.exception(f"An unexpected error occurred during web search: {e!s}")
        msg = f"An unexpected error occurred: {e!s}"
        raise ValueError(msg) from e


def process_data(config: ActionConfig, *, debug: bool = False) -> dict[str, Any]:
    """Process the input data according to the provided action configuration.

    Args:
        config: The Pydantic model containing action type, parameters, and API keys.
        debug: Enable debug mode.

    Returns:
        Processed data as a dictionary.

    Raises:
        ValueError: If configuration is invalid or action type is unsupported.
    """
    if debug:
        logger.setLevel(logging.DEBUG)
        logger.debug(
            f"Debug mode enabled. Received config: {config.model_dump_json(indent=2)}"
        )

    if config.action_type == "enrich_person":
        if not isinstance(config.parameters, PersonEnrichmentParams):
            msg = "Invalid parameters for 'enrich_person' action."
            raise ValueError(msg)
        return _handle_enrich_person(config.parameters, config.api_keys)

    elif config.action_type == "search_web":
        if not isinstance(config.parameters, WebSearchParams):
            msg = "Invalid parameters for 'search_web' action."
            raise ValueError(msg)
        return _handle_search_web(config.parameters, config.api_keys)

    else:
        msg = f"Unsupported action type: {config.action_type}"
        raise ValueError(msg)


#
# The main() function and its associated if __name__ == "__main__": block
# have been moved to examples/run_action_config_example.py
# to keep this file focused on library code.
#
