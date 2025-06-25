# Person Profile API Integration (Summary)

This document outlines the approach for integrating person profile enrichment APIs within the `twat-llm` library.

## Primary API Choice: Proxycurl

For the MVP, `twat-llm` primarily utilizes **Proxycurl** for fetching detailed professional profile data, especially from LinkedIn.

**Key Features Leveraged:**
*   Resolving LinkedIn profiles from URLs.
*   Extracting information such as job history, education, skills, and contact details.

**Usage within `twat-llm`:**
*   The `enrich_person` action in `src/twat_llm/twat_llm.py` handles interaction with Proxycurl.
*   Requires `PROXYCURL_API_KEY` to be set in the environment or a `.env` file.
*   Fetched data is then summarized by an LLM via the `mallmo.py` module to provide a concise overview.

## Considerations
*   **Data Privacy & Terms of Service:** Users of `twat-llm` should be aware of Proxycurl's terms of service and data usage policies, as well as any privacy implications (e.g., GDPR, CCPA) when processing personal data.
*   **API Key Management:** Securely manage your Proxycurl API key.
*   **Error Handling:** The library includes error handling for API request failures.

## Future Enhancements (Post-MVP)
*   Support for other person data enrichment services.
*   More sophisticated lookup mechanisms (e.g., finding profiles by name/email if a LinkedIn URL isn't provided).
*   Allowing users to customize the LLM summarization prompt for profile data.

*This summary replaces a more detailed internal research document comparing various People APIs. For specific details on Proxycurl's API capabilities, refer to the official Proxycurl documentation.*
