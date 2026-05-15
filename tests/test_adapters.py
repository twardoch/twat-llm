"""Tests for stable twat_text adapter functions."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

from twat_llm.adapters import adapter_call, classify_text, extract_structured_data, rewrite_text, summarize_text


@patch("twat_llm.adapters.ask", return_value="short summary")
def test_summarize_text_calls_ask(mock_ask: Any) -> None:
    """summarize_text builds a summarization prompt and forwards text as data."""

    result = summarize_text("Long text", model_ids=["model-a"])

    assert result == "short summary"
    mock_ask.assert_called_once()
    assert mock_ask.call_args.kwargs["data"] == "Long text"
    assert mock_ask.call_args.kwargs["model_ids"] == ["model-a"]


@patch("twat_llm.adapters.ask", return_value="formal text")
def test_rewrite_text_requires_instruction_and_calls_ask(mock_ask: Any) -> None:
    """rewrite_text includes caller instruction in the prompt."""

    result = rewrite_text("hey", instruction="Make it formal")

    assert result == "formal text"
    assert "Make it formal" in mock_ask.call_args.kwargs["prompt"]


@patch("twat_llm.adapters.ask", return_value='{"name":"Ada"}')
def test_extract_structured_data_calls_ask(mock_ask: Any) -> None:
    """extract_structured_data includes schema hints."""

    result = extract_structured_data("Ada Lovelace", schema_hint="Return name only")

    assert result == '{"name":"Ada"}'
    assert "Return name only" in mock_ask.call_args.kwargs["prompt"]


@patch("twat_llm.adapters.ask", return_value="positive")
def test_classify_text_calls_ask(mock_ask: Any) -> None:
    """classify_text lists labels in the prompt."""

    result = classify_text("Great", labels=["positive", "negative"])

    assert result == "positive"
    assert "positive, negative" in mock_ask.call_args.kwargs["prompt"]


def test_classify_text_requires_labels() -> None:
    """classify_text rejects empty label sets."""

    with pytest.raises(ValueError, match="At least one label"):
        classify_text("text", labels=[])


@patch("twat_llm.adapters.summarize_text", return_value="summary")
def test_adapter_call_dispatches(mock_summarize: Any) -> None:
    """adapter_call provides a stable named dispatch surface."""

    assert adapter_call("summarize", "text") == "summary"
    mock_summarize.assert_called_once()
