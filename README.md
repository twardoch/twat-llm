# twat-llm

## Features

- Modern Python packaging with PEP 621 compliance
- Type hints and runtime type checking
- Comprehensive test suite and documentation
- CI/CD ready configuration

## Installation

```bash
pip install twat-llm
```

## Usage

The `twat-llm` library provides functionality to process data using LLMs, potentially interacting with external APIs for enrichment and search.

```python
import twat_llm

# Example (conceptual, actual API will be refined)
config_enrich_person = {
    "action": "enrich_person",
    "params": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        # API keys would be handled securely, e.g., via environment variables or a config file
    }
}
enriched_data = twat_llm.process_data(config_enrich_person)
print(enriched_data)

config_search_web = {
    "action": "search_web",
    "params": {
        "query": "latest advancements in AI",
    }
}
search_summary = twat_llm.process_data(config_search_web)
print(search_summary)
```

More detailed usage examples will be provided as the API is finalized.

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management.

### Setup Development Environment

```bash
# Install hatch if you haven't already
pip install hatch

# Create and activate development environment
hatch shell

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run linting
hatch run lint

# Format code
hatch run format
```

## License

MIT License  
.
