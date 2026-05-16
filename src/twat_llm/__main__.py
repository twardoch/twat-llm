# this_file: src/twat_llm/__main__.py
"""Fire CLI entry point for twat-llm."""

from __future__ import annotations

import sys

import fire


# ---------------------------------------------------------------------------
# Leaf implementations (lazy imports so --help is instant)
# ---------------------------------------------------------------------------


def _ask(
    prompt: str,
    data: str | None = None,
    model: str | None = None,
    media: list[str] | None = None,
    verbose: bool = False,
) -> str:
    """Send a prompt to an LLM and print the response.

    Args:
        prompt: The text prompt to send.
        data: Optional input data appended/interpolated into the prompt.
        model: Model ID to use (default: gpt-4o-mini with fallbacks).
        media: Optional image file paths to attach (JPEG/PNG/GIF/WebP).
        verbose: Enable debug logging.
    """
    if verbose:
        from loguru import logger

        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    from twat_llm.mallmo import ask

    model_ids = [model] if model else None
    from pathlib import Path

    media_paths = [Path(p) for p in media] if media else None
    result = ask(prompt=prompt, data=data, model_ids=model_ids, media_paths=media_paths)
    print(result)
    return result


def _complete(
    prompt: str,
    data: str | None = None,
    model: str | None = None,
    verbose: bool = False,
) -> str:
    """Complete a prompt using an LLM (alias for ask without media).

    Args:
        prompt: The text prompt to complete.
        data: Optional input data appended/interpolated into the prompt.
        model: Model ID to use (default: gpt-4o-mini with fallbacks).
        verbose: Enable debug logging.
    """
    return _ask(prompt=prompt, data=data, model=model, verbose=verbose)


def _ask_batch(
    prompts_file: str,
    output_file: str | None = None,
    model: str | None = None,
    processes: int | None = None,
    verbose: bool = False,
) -> None:
    """Process multiple prompts from a file in parallel.

    Args:
        prompts_file: Path to file with one prompt per line.
        output_file: Optional path to write responses (one per line).
        model: Model ID to use.
        processes: Number of parallel processes (default: CPU count).
        verbose: Enable debug logging.
    """
    if verbose:
        from loguru import logger

        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    from pathlib import Path
    from twat_llm.mallmo import ask_batch

    p = Path(prompts_file).expanduser()
    prompts = [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not prompts:
        print("No prompts found.", file=sys.stderr)
        return

    model_ids = [model] if model else None
    results = ask_batch(prompts, model_ids=model_ids, num_processes=processes)

    if output_file:
        out = Path(output_file).expanduser()
        out.write_text("\n".join(results) + "\n", encoding="utf-8")
        print(f"Wrote {len(results)} responses to {out}")
    else:
        for r in results:
            print(r)


def _ask_chain(
    data: str,
    steps: list[str],
    model: str | None = None,
    verbose: bool = False,
) -> str:
    """Pipe data through a sequence of prompt steps.

    Args:
        data: Initial input string.
        steps: Ordered list of prompt strings (each receives previous output).
        model: Model ID to use for all steps.
        verbose: Enable debug logging.
    """
    if verbose:
        from loguru import logger

        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    from twat_llm.mallmo import ask_chain

    # Note: model selection per-step is not yet supported by ask_chain;
    # the default fallback chain in mallmo.ask is used for each step.
    result = ask_chain(data=data, steps=steps)
    print(result)
    return result


def _list_models(verbose: bool = False) -> None:
    """List all available LLM models installed via the llm library.

    Args:
        verbose: Enable debug logging.
    """
    if verbose:
        from loguru import logger

        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    import llm

    models = llm.get_models()
    for m in models:
        print(m.model_id)


def _version() -> str:
    """Print the twat-llm package version."""
    from twat_llm.__version__ import __version__

    print(__version__)
    return __version__


# ---------------------------------------------------------------------------
# COMMANDS dict — explicit allow-list
# ---------------------------------------------------------------------------

COMMANDS: dict[str, object] = {
    "ask": _ask,
    "complete": _complete,
    "ask-batch": _ask_batch,
    "ask-chain": _ask_chain,
    "list-models": _list_models,
    "version": _version,
}


# ---------------------------------------------------------------------------
# Top-level dispatcher
# ---------------------------------------------------------------------------


def main() -> None:
    """Fire CLI dispatcher for twat-llm."""
    fire.Fire(COMMANDS, name="twat-llm")


# ---------------------------------------------------------------------------
# Per-leaf dashed-entry helpers
# ---------------------------------------------------------------------------


def cmd_ask() -> None:
    """Entry point for twat-llm-ask."""
    fire.Fire(_ask, name="twat-llm-ask")


def cmd_complete() -> None:
    """Entry point for twat-llm-complete."""
    fire.Fire(_complete, name="twat-llm-complete")


def cmd_ask_batch() -> None:
    """Entry point for twat-llm-ask-batch."""
    fire.Fire(_ask_batch, name="twat-llm-ask-batch")


def cmd_ask_chain() -> None:
    """Entry point for twat-llm-ask-chain."""
    fire.Fire(_ask_chain, name="twat-llm-ask-chain")


def cmd_list_models() -> None:
    """Entry point for twat-llm-list-models."""
    fire.Fire(_list_models, name="twat-llm-list-models")


def cmd_version() -> None:
    """Entry point for twat-llm-version."""
    fire.Fire(_version, name="twat-llm-version")


if __name__ == "__main__":
    main()
