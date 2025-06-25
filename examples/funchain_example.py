#!/usr/bin/env python3
"""
Example script to demonstrate the ask_chain functionality from twat_llm.mallmo.

This script shows how to chain multiple processing steps, where each step can be
an LLM prompt (string) or a Python callable.

Requirements:
- Ensure the `twat-llm` package is installed.
- Ensure you have LLM models configured for the `llm` library, as `ask_chain`
  will use them for string-based prompt steps.
  See https://llm.datasette.io/en/stable/models/index.html for model setup.
"""
from __future__ import annotations

import logging

# Configure basic logging for the example
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from twat_llm.mallmo import ask_chain, LLMError
except ImportError:
    logger.error(
        "Failed to import ask_chain from twat_llm.mallmo. "
        "Ensure 'twat-llm' is installed and accessible."
    )
    raise


def to_lower_case(text_input: str) -> str:
    """Converts a string to lower case. Simple callable example."""
    logger.info(f"Converting to lower case: '{text_input}'")
    return text_input.lower()

def main():
    """Runs the ask_chain example."""
    initial_data = "My name is Adam Twardoch"
    logger.info(f"Initial data for chain: '{initial_data}'")

    # Define the processing steps
    # Step 1: LLM prompt to convert to all caps
    # Step 2: LLM prompt to translate the result into Polish
    # Step 3: Python callable to convert the Polish translation to lower case
    processing_steps = [
        "Convert the full name to all caps in: $input",  # $input will be initial_data
        "Translate into Polish:",  # Input will be the result of the previous step
        to_lower_case,             # Input will be the Polish translation
    ]

    try:
        logger.info("Starting ask_chain process...")
        final_output = ask_chain(
            data=initial_data,
            steps=processing_steps
        )
        logger.info("\n--- FunChain Example Result ---")
        print(f"Initial Data: {initial_data}") # noqa: T201
        print(f"Steps: {processing_steps}") # noqa: T201
        print(f"Final Output: {final_output}") # noqa: T201

    except LLMError as e:
        logger.error(f"An LLM-related error occurred in the chain: {e}")
        print(f"LLM Error: {e}") # noqa: T201
        print("Please ensure your `llm` models are correctly configured.") # noqa: T201
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        print(f"An unexpected error occurred: {e}") # noqa: T201

if __name__ == "__main__":
    main()
    print("\nFunChain example finished.") # noqa: T201
    print("Ensure your `llm` library is configured with models for the prompt steps.") # noqa: T201
