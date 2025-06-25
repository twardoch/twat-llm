# Web Search API Integration (Summary)

This document outlines the approach for integrating web search APIs within the `twat-llm` library.

## Primary API Choice (Example): Brave Search API

For the MVP, `twat-llm` demonstrates web search capabilities using the **Brave Search API** as a primary example. The implementation can be adapted for other search providers.

**Key Features Leveraged:**
*   Performing web searches based on user queries.
*   Retrieving a list of search results, including titles, snippets, and URLs.

**Usage within `twat-llm`:**
*   The `search_web` action in `src/twat_llm/twat_llm.py` handles interaction with the chosen search API (e.g., Brave Search).
*   Requires a `SEARCH_API_KEY` (specific to the chosen provider, e.g., Brave's `X-Subscription-Token`) to be set in the environment or a `.env` file.
*   Fetched search results are then summarized by an LLM via the `mallmo.py` module to provide a concise answer or overview related to the query.

## Considerations
*   **API Provider Choice:** While Brave Search is used as an example, users might configure other providers. The `SEARCH_API_KEY` and specific API endpoint/parameters in `twat_llm.py` would need adjustment.
*   **Terms of Service:** Users must adhere to the terms of service of their chosen web search API provider.
*   **Rate Limits & Quotas:** Be mindful of API rate limits and query quotas.
*   **Result Quality:** The relevance and quality of search results depend on the chosen API provider.
*   **Cost:** Web search APIs typically have costs associated with their usage.

## Future Enhancements (Post-MVP)
*   Easier configuration for multiple search API providers.
*   More sophisticated parsing and ranking of search results before LLM summarization.
*   Allowing users to customize the LLM summarization prompt for search results.

*This summary replaces a more detailed internal research document comparing various Web Search APIs. For specific details on the Brave Search API, refer to the official Brave Search API documentation. If using another provider, consult their respective documentation.*
