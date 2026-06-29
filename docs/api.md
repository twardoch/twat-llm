# API Reference

## `twat_llm.mallmo` — core LLM helpers

### `ask`

```python
ask(
    prompt: str,
    data: str | None = None,
    model_ids: Sequence[str] | None = None,
    media_paths: Sequence[Path | str] | None = None,
) -> str
```

Send a prompt to an LLM and return the text reply.

**Parameters**

| Name | Type | Description |
|---|---|---|
| `prompt` | `str` | The instruction or question to send. |
| `data` | `str \| None` | Optional text to incorporate. If the prompt contains `$input`, data replaces it; otherwise data is appended after the prompt. |
| `model_ids` | `list[str] \| None` | Models to try in order. Defaults to `DEFAULT_FALLBACK_MODELS` (`gpt-4o-mini`, Gemini Flash, Claude Haiku). |
| `media_paths` | `list[Path \| str] \| None` | Image files to attach (JPEG, PNG, GIF, WebP, BMP, TIFF). Images are resized to 512 × 512 before sending. |

**Returns** `str` — the model's text response.

**Raises** `LLMError` if every model in `model_ids` fails.

---

### `ask_chain`

```python
ask_chain(
    data: str,
    steps: Iterable[str | Callable | tuple[str | Callable, dict]],
) -> str
```

Pipe `data` through a sequence of steps. Each step's output becomes the next step's input.

A step can be:
- A **string** — used as a prompt (calls `ask(prompt=step, data=current)`).
- A **callable** — called as `step(current_data)`.
- A **tuple** `(processor, kwargs)` — called as `processor(current_data, **kwargs)`.

---

### `ask_batch`

```python
ask_batch(
    prompts: Sequence[str],
    model_ids: Sequence[str] | None = None,
    num_processes: int | None = None,
) -> list[str]
```

Process multiple prompts in parallel using `ProcessPoolExecutor`.

**Note:** media attachments are not supported in batch mode.

---

### Exception classes

| Class | Meaning |
|---|---|
| `LLMError` | Base class — all models failed |
| `ModelInvocationError` | A single model call failed |
| `MediaProcessingError` | Image could not be read/resized |
| `BatchProcessingError` | Parallel batch execution failed |

---

## `twat_llm.adapters` — stable text-operation surface

### `summarize_text`

```python
summarize_text(
    text: str,
    *,
    instruction: str | None = None,
    model_ids: Sequence[str] | None = None,
) -> str
```

Summarise `text`. An optional `instruction` overrides the default "Summarize clearly and concisely" prompt.

---

### `rewrite_text`

```python
rewrite_text(
    text: str,
    *,
    instruction: str,
    model_ids: Sequence[str] | None = None,
) -> str
```

Rewrite `text` according to `instruction` (e.g. `"Make it formal"`, `"Shorten to one sentence"`).

---

### `extract_structured_data`

```python
extract_structured_data(
    text: str,
    *,
    schema_hint: str = "Return concise JSON with the requested fields.",
    model_ids: Sequence[str] | None = None,
) -> str
```

Ask the model to extract structured data from `text`. The `schema_hint` tells the model what fields to return (returned as a raw JSON string — parse with `json.loads`).

---

### `classify_text`

```python
classify_text(
    text: str,
    *,
    labels: Sequence[str],
    model_ids: Sequence[str] | None = None,
) -> str
```

Classify `text` into exactly one of the provided `labels`. Raises `ValueError` if `labels` is empty.

---

### `adapter_call`

```python
adapter_call(operation: str, text: str, **kwargs) -> str
```

Dispatch by name: `"summarize"`, `"rewrite"`, `"extract"`, or `"classify"`.

---

## `twat_llm.twat_llm` — high-level actions

### `process_data`

```python
process_data(config: ActionConfig, *, debug: bool = False) -> dict[str, Any]
```

Execute an action defined by `config` and return a result dictionary.

**`ActionConfig` fields**

| Field | Type | Description |
|---|---|---|
| `action_type` | `"enrich_person" \| "search_web"` | Which action to run |
| `parameters` | `PersonEnrichmentParams \| WebSearchParams` | Action-specific parameters |
| `api_keys` | `ApiKeySettings` | API keys (loaded from env by default) |

**`enrich_person` result keys:** `status`, `action`, `linkedin_url`, `raw_profile_data`, `summary`

**`search_web` result keys:** `status`, `action`, `query`, `raw_search_results`, `summary`

### Required environment variables

| Variable | Used by |
|---|---|
| `PROXYCURL_API_KEY` | `enrich_person` action |
| `SEARCH_API_KEY` | `search_web` action |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / etc. | LLM model calls via `llm` library |
