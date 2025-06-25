"""Test suite for twat_llm."""

import pytest
from unittest.mock import patch, MagicMock
import pydantic  # Added for ValidationError
import httpx  # Added for HTTPStatusError and RequestError

# Assuming your Pydantic models and process_data are in src.twat_llm.twat_llm
# Adjust the import path if your structure is different after hatch build/install
from twat_llm.twat_llm import (
    ActionConfig,
    ApiKeySettings,
    PersonEnrichmentParams,
    WebSearchParams,
    process_data,
)
import twat_llm  # Moved import to top-level


def test_version():
    """Verify package exposes version."""
    # import twat_llm # Moved to top-level
    assert twat_llm.__version__


# --- Pydantic Model Tests ---


def test_action_config_enrich_person_valid():
    """Test valid ActionConfig for person enrichment."""
    config_data = {
        "action_type": "enrich_person",
        "parameters": {"name": "John Doe", "email": "john@example.com"},
    }
    config = ActionConfig(**config_data)
    assert config.action_type == "enrich_person"
    assert isinstance(config.parameters, PersonEnrichmentParams)
    assert config.parameters.name == "John Doe"


def test_action_config_search_web_valid():
    """Test valid ActionConfig for web search."""
    config_data = {"action_type": "search_web", "parameters": {"query": "test query"}}
    config = ActionConfig(**config_data)
    assert config.action_type == "search_web"
    assert isinstance(config.parameters, WebSearchParams)
    assert config.parameters.query == "test query"


def test_action_config_invalid_action_type():
    """Test ActionConfig with an invalid action type."""
    config_data = {
        "action_type": "unknown_action",
        "parameters": {"query": "test query"},
    }
    with pytest.raises(ValueError):  # Pydantic raises ValueError for invalid Literal
        ActionConfig(**config_data)


def test_action_config_enrich_person_missing_params():
    """Test ActionConfig for enrich_person with missing required parameters (if any)."""
    # PersonEnrichmentParams has all optional fields for now, so this might pass.
    # If fields become mandatory, this test would need adjustment.
    config_data = {"action_type": "enrich_person", "parameters": {}}
    config = ActionConfig(**config_data)
    assert isinstance(config.parameters, PersonEnrichmentParams)


def test_action_config_search_web_missing_query():
    """Test ActionConfig for search_web with missing query."""
    config_data = {
        "action_type": "search_web",
        "parameters": {},  # Missing 'query'
    }
    with pytest.raises(
        pydantic.ValidationError
    ):  # Pydantic raises ValidationError for missing fields
        ActionConfig(**config_data)


# --- ApiKeySettings Tests ---


def test_api_key_settings_load_from_env(monkeypatch):
    """Test ApiKeySettings loads from environment variables."""
    monkeypatch.setenv("PROXYCURL_API_KEY", "test_proxycurl_key")
    monkeypatch.setenv("SEARCH_API_KEY", "test_search_key")

    settings = ApiKeySettings()
    assert settings.proxycurl_api_key == "test_proxycurl_key"
    assert settings.search_api_key == "test_search_key"


def test_api_key_settings_no_env():
    """Test ApiKeySettings when no environment variables are set."""
    # Assuming no relevant env vars are set by default in the test environment
    settings = ApiKeySettings()
    assert settings.proxycurl_api_key is None
    assert settings.search_api_key is None


# --- process_data Tests (to be expanded) ---

# Placeholder for further tests - we will build these out
# For now, the structure for process_data tests will be set up.


@patch("twat_llm.twat_llm.httpx.Client")
@patch("twat_llm.twat_llm.ask")
def test_process_data_enrich_person_success(
    mock_mallmo_ask, mock_http_client, monkeypatch
):
    """Test successful person enrichment."""
    monkeypatch.setenv("PROXYCURL_API_KEY", "fake_proxy_key")

    # Mock Proxycurl API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "linkedin_profile": "data",
        "full_name": "John Doe",
    }

    # Configure the mock client instance
    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.return_value = mock_response

    # Mock mallmo.ask response
    mock_mallmo_ask.return_value = "LLM summary of profile"

    config = ActionConfig(
        action_type="enrich_person",
        parameters=PersonEnrichmentParams(
            linkedin_profile_url="http://linkedin.com/in/johndoe"
        ),
    )

    result = process_data(config)

    assert result["status"] == "success"
    assert result["summary"] == "LLM summary of profile"
    assert result["raw_profile_data"]["full_name"] == "John Doe"
    mock_client_instance.get.assert_called_once()
    # Ensure the prompt sent to mallmo.ask is reasonable
    call_kwargs = mock_mallmo_ask.call_args.kwargs
    assert (
        "John Doe" in call_kwargs["prompt"]
    )  # Check if some profile data is in the prompt
    mock_mallmo_ask.assert_called_once()


def test_process_data_enrich_person_missing_api_key(monkeypatch):
    """Test person enrichment when PROXYCURL_API_KEY is missing."""
    monkeypatch.delenv("PROXYCURL_API_KEY", raising=False)  # Ensure it's not set
    config = ActionConfig(
        action_type="enrich_person",
        parameters=PersonEnrichmentParams(
            linkedin_profile_url="http://linkedin.com/in/johndoe"
        ),  # type: ignore
    )
    with pytest.raises(ValueError, match="PROXYCURL_API_KEY is required"):
        process_data(config)


def test_process_data_enrich_person_missing_linkedin_url(monkeypatch):
    """Test person enrichment when LinkedIn URL is missing (as per MVP)."""
    monkeypatch.setenv("PROXYCURL_API_KEY", "fake_proxy_key")
    config = ActionConfig(
        action_type="enrich_person",
        parameters=PersonEnrichmentParams(name="John Doe"),  # No URL
    )
    with pytest.raises(ValueError, match="LinkedIn profile URL is required"):
        process_data(config)


@patch("twat_llm.twat_llm.httpx.Client")
def test_process_data_enrich_person_api_http_error(mock_http_client, monkeypatch):
    """Test person enrichment when Proxycurl API returns an HTTP error."""
    monkeypatch.setenv("PROXYCURL_API_KEY", "fake_proxy_key")

    mock_response = MagicMock()
    mock_response.status_code = 401  # Unauthorized
    mock_response.text = "Invalid API key"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Client error '401 Unauthorized'", request=MagicMock(), response=mock_response
    )

    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.return_value = mock_response

    config = ActionConfig(
        action_type="enrich_person",
        parameters=PersonEnrichmentParams(
            linkedin_profile_url="http://linkedin.com/in/johndoe"
        ),  # type: ignore
    )

    with pytest.raises(ValueError, match="Failed to retrieve data from Proxycurl"):
        process_data(config)


@patch("twat_llm.twat_llm.httpx.Client")
def test_process_data_enrich_person_api_request_error(mock_http_client, monkeypatch):
    """Test person enrichment when there's a request error (e.g., network)."""
    monkeypatch.setenv("PROXYCURL_API_KEY", "fake_proxy_key")

    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.side_effect = httpx.RequestError(
        "Network error", request=MagicMock()
    )

    config = ActionConfig(
        action_type="enrich_person",
        parameters=PersonEnrichmentParams(
            linkedin_profile_url="http://linkedin.com/in/johndoe"
        ),  # type: ignore
    )

    with pytest.raises(ValueError, match="Failed to connect to Proxycurl"):
        process_data(config)


@patch("twat_llm.twat_llm.httpx.Client")
@patch("twat_llm.twat_llm.ask")
def test_process_data_enrich_person_mallmo_error(
    mock_mallmo_ask, mock_http_client, monkeypatch
):
    """Test person enrichment when mallmo.ask raises an error."""
    monkeypatch.setenv("PROXYCURL_API_KEY", "fake_proxy_key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "linkedin_profile": "data",
        "full_name": "John Doe",
    }

    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.return_value = mock_response

    mock_mallmo_ask.side_effect = Exception("LLM unavailable")

    config = ActionConfig(
        action_type="enrich_person",
        parameters=PersonEnrichmentParams(
            linkedin_profile_url="http://linkedin.com/in/johndoe"
        ),  # type: ignore
    )

    with pytest.raises(
        ValueError, match="An unexpected error occurred"
    ):  # General error wrapping
        process_data(config)


# --- Tests for search_web action ---


@patch("twat_llm.twat_llm.httpx.Client")
@patch("twat_llm.twat_llm.ask")
def test_process_data_search_web_success(
    mock_mallmo_ask, mock_http_client, monkeypatch
):
    """Test successful web search."""
    monkeypatch.setenv("SEARCH_API_KEY", "fake_search_key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"web": {"results": [{"title": "Test Result"}]}}

    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.return_value = mock_response

    mock_mallmo_ask.return_value = "LLM summary of search results"

    config = ActionConfig(
        action_type="search_web", parameters=WebSearchParams(query="test query")
    )

    result = process_data(config)

    assert result["status"] == "success"
    assert result["summary"] == "LLM summary of search results"
    assert result["raw_search_results"]["web"]["results"][0]["title"] == "Test Result"
    mock_client_instance.get.assert_called_once()
    # Ensure the prompt sent to mallmo.ask is reasonable
    call_kwargs = mock_mallmo_ask.call_args.kwargs
    assert (
        "Test Result" in call_kwargs["prompt"]
    )  # Check if some search data is in the prompt
    mock_mallmo_ask.assert_called_once()


def test_process_data_search_web_missing_api_key(monkeypatch):
    """Test web search when SEARCH_API_KEY is missing."""
    monkeypatch.delenv("SEARCH_API_KEY", raising=False)
    config = ActionConfig(
        action_type="search_web", parameters=WebSearchParams(query="test query")
    )
    with pytest.raises(ValueError, match="SEARCH_API_KEY is required"):
        process_data(config)


@patch("twat_llm.twat_llm.httpx.Client")
def test_process_data_search_web_api_http_error(mock_http_client, monkeypatch):
    """Test web search when Search API returns an HTTP error."""
    monkeypatch.setenv("SEARCH_API_KEY", "fake_search_key")

    mock_response = MagicMock()
    mock_response.status_code = 403  # Forbidden
    mock_response.text = "Subscription inactive"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Client error '403 Forbidden'", request=MagicMock(), response=mock_response
    )

    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.return_value = mock_response

    config = ActionConfig(
        action_type="search_web", parameters=WebSearchParams(query="test query")
    )

    with pytest.raises(ValueError, match="Failed to retrieve data from Search API"):
        process_data(config)


@patch("twat_llm.twat_llm.httpx.Client")
def test_process_data_search_web_api_request_error(mock_http_client, monkeypatch):
    """Test web search when there's a request error."""
    monkeypatch.setenv("SEARCH_API_KEY", "fake_search_key")

    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.side_effect = httpx.RequestError(
        "Connection refused", request=MagicMock()
    )

    config = ActionConfig(
        action_type="search_web", parameters=WebSearchParams(query="test query")
    )

    with pytest.raises(ValueError, match="Failed to connect to Search API"):
        process_data(config)


@patch("twat_llm.twat_llm.httpx.Client")
@patch("twat_llm.twat_llm.ask")
def test_process_data_search_web_mallmo_error(
    mock_mallmo_ask, mock_http_client, monkeypatch
):
    """Test web search when mallmo.ask raises an error."""
    monkeypatch.setenv("SEARCH_API_KEY", "fake_search_key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"web": {"results": [{"title": "Test Result"}]}}

    mock_client_instance = mock_http_client.return_value.__enter__.return_value
    mock_client_instance.get.return_value = mock_response

    mock_mallmo_ask.side_effect = Exception("LLM processing failed")

    config = ActionConfig(
        action_type="search_web", parameters=WebSearchParams(query="test query")
    )

    with pytest.raises(ValueError, match="An unexpected error occurred"):
        process_data(config)
