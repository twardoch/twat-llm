"""Stable text-operation adapters used by twat_text.

# this_file: src/twat_llm/adapters.py
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field

from twat_llm.mallmo import ask


class TextOperationRequest(BaseModel):
    """Input for text-heavy LLM operations."""

    text: str = Field(..., min_length=1)
    instruction: str | None = None
    model_ids: list[str] | None = None
    schema_hint: str | None = None
    labels: list[str] | None = None


def _call_ask(prompt: str, request: TextOperationRequest) -> str:
    """Call mallmo.ask using the stable request shape."""

    return str(ask(prompt=prompt, data=request.text, model_ids=request.model_ids))


def summarize_text(text: str, *, instruction: str | None = None, model_ids: Sequence[str] | None = None) -> str:
    """Summarize text using the configured LLM provider fallback chain."""

    request = TextOperationRequest(text=text, instruction=instruction, model_ids=list(model_ids) if model_ids else None)
    prompt = instruction or "Summarize the following text clearly and concisely: $input"
    return _call_ask(prompt, request)


def rewrite_text(text: str, *, instruction: str, model_ids: Sequence[str] | None = None) -> str:
    """Rewrite text according to a caller-provided instruction."""

    request = TextOperationRequest(text=text, instruction=instruction, model_ids=list(model_ids) if model_ids else None)
    return _call_ask(f"{instruction}\n\nText to rewrite:\n$input", request)


def extract_structured_data(
    text: str,
    *,
    schema_hint: str = "Return concise JSON with the requested fields.",
    model_ids: Sequence[str] | None = None,
) -> str:
    """Extract structured data from text and return the provider's JSON-like response."""

    request = TextOperationRequest(text=text, schema_hint=schema_hint, model_ids=list(model_ids) if model_ids else None)
    return _call_ask(f"Extract structured data from this text. {schema_hint}\n\n$input", request)


def classify_text(text: str, *, labels: Sequence[str], model_ids: Sequence[str] | None = None) -> str:
    """Classify text into one of the supplied labels."""

    if not labels:
        msg = "At least one label is required for classification."
        raise ValueError(msg)
    request = TextOperationRequest(text=text, labels=list(labels), model_ids=list(model_ids) if model_ids else None)
    label_list = ", ".join(labels)
    return _call_ask(f"Classify the text as exactly one of these labels: {label_list}.\n\n$input", request)


def adapter_call(operation: str, text: str, **kwargs: Any) -> str:
    """Dispatch a named adapter operation for narrow integrations."""

    if operation == "summarize":
        return summarize_text(text, instruction=kwargs.get("instruction"), model_ids=kwargs.get("model_ids"))
    if operation == "rewrite":
        instruction = kwargs.get("instruction")
        if not instruction:
            msg = "rewrite requires an instruction."
            raise ValueError(msg)
        return rewrite_text(text, instruction=instruction, model_ids=kwargs.get("model_ids"))
    if operation == "extract":
        return extract_structured_data(
            text, schema_hint=kwargs.get("schema_hint", "Return JSON."), model_ids=kwargs.get("model_ids")
        )
    if operation == "classify":
        return classify_text(text, labels=kwargs.get("labels", []), model_ids=kwargs.get("model_ids"))
    msg = f"Unsupported text adapter operation: {operation}"
    raise ValueError(msg)


__all__ = [
    "TextOperationRequest",
    "adapter_call",
    "classify_text",
    "extract_structured_data",
    "rewrite_text",
    "summarize_text",
]
