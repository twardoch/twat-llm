# SPDX-FileCopyrightText: 2024 Adam Twardoch <adam+github@twardoch.com>
#
# SPDX-License-Identifier: MIT

from .__version__ import __version__

"""twat-llm: LLM integration for twat."""

from __future__ import annotations


# Expose main functionalities for the library user
from twat_llm.mallmo import (
    BatchProcessingError,
    LLMError,
    MediaProcessingError,
    ModelInvocationError,
    ask,
    ask_batch,
    ask_chain,
)
from twat_llm.adapters import (
    TextOperationRequest,
    adapter_call,
    classify_text,
    extract_structured_data,
    rewrite_text,
    summarize_text,
)
from twat_llm.twat_llm import (
    ActionConfig,
    ApiKeySettings,
    PersonEnrichmentParams,
    WebSearchParams,
    process_data,
)


def main() -> None:
    """CLI entry point for twat-llm."""
    print(f"twat-llm v{__version__}")


__all__ = [
    "ActionConfig",
    "ApiKeySettings",
    "BatchProcessingError",
    "LLMError",
    "MediaProcessingError",
    "ModelInvocationError",
    "PersonEnrichmentParams",
    "TextOperationRequest",
    "WebSearchParams",
    "__version__",
    "adapter_call",
    "ask",
    "ask_batch",
    "ask_chain",
    "classify_text",
    "extract_structured_data",
    "main",
    "process_data",
    "rewrite_text",
    "summarize_text",
]
