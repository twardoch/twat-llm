# twat-llm

**twat-llm** is the LLM integration plugin for the [twat](https://github.com/twardoch/twat) ecosystem. It lets you send text (and images) to any Large Language Model (LLM), chain multiple calls together, and process batches in parallel — all through a single, consistent API.

## What is an LLM?

A **Large Language Model** (LLM) is an AI system trained on text that can read a question or instruction and write a coherent reply. Familiar examples are OpenAI's GPT-4o, Anthropic's Claude, and Google's Gemini. Under the hood, `twat-llm` uses Simon Willison's [`llm`](https://llm.datasette.io) library, which supports dozens of LLM providers through installable plugins.

## What does `twat-llm` do with your text?

When you call `ask("Summarise this article", data=long_text)`, the library:

1. **Builds a prompt** — combines your instruction with the data you supply.
2. **Selects a model** — tries models in priority order, falling back automatically if one fails.
3. **Sends the request** — calls the model's API and waits for the reply.
4. **Returns plain text** — the model's response as a Python string.

Image files can also be attached for multimodal prompts (resized to 512 × 512 before sending to keep costs low).

## Quick start

```bash
pip install twat-llm
```

Set your LLM provider API key (example for OpenAI):

```bash
export OPENAI_API_KEY="sk-..."
```

```python
from twat_llm import ask

reply = ask("What is the capital of France?")
print(reply)  # Paris
```

## Core functions

| Function | What it does |
|---|---|
| `ask(prompt, data, model_ids, media_paths)` | Send one prompt, get one reply. Tries models in order until one works. |
| `ask_chain(data, steps)` | Pipe text through a sequence of prompt steps or Python functions. |
| `ask_batch(prompts, model_ids, num_processes)` | Process many prompts in parallel using multiple CPU cores. |

## Stable text adapters (used by `twat-text`)

These four functions form a narrow, stable interface consumed by the `twat_text` package:

| Function | Purpose |
|---|---|
| `summarize_text(text)` | Condense text to its key points |
| `rewrite_text(text, instruction=…)` | Rephrase text according to an instruction |
| `extract_structured_data(text, schema_hint=…)` | Pull structured JSON from unstructured text |
| `classify_text(text, labels=[…])` | Assign text to one of the provided categories |

Use `adapter_call(operation, text, **kwargs)` for a single dispatch point.

## High-level actions

`process_data(ActionConfig(…))` runs predefined multi-step workflows:

- **`enrich_person`** — fetch a LinkedIn profile via Proxycurl, then summarise it with an LLM (requires `PROXYCURL_API_KEY`).
- **`search_web`** — run a query through Brave Search, then summarise the results (requires `SEARCH_API_KEY`).

## CLI

```bash
twat-llm ask --prompt "Translate to French" --data "Hello world"
twat-llm ask-batch --prompts-file prompts.txt --output-file responses.txt
twat-llm ask-chain --data "raw text" --steps "Summarise" "Translate to Spanish"
twat-llm list-models
twat-llm version
```

## Role in the twat ecosystem

`twat-llm` owns **text-heavy LLM work**: prompts, chat calls, chains, batches, and text-centric multimodal analysis. It registers as `twat.plugins.llm` so the host `twat` package discovers it automatically.

- Generated media (images, video) → `twat-genai`
- Deterministic text algorithms → `twat-text`
- File upload/download → `twat-fs`
