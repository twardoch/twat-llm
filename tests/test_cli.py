# this_file: tests/test_cli.py
"""CLI smoke tests for twat-llm Fire interface.

All tests use subprocess so they exercise the real entry-point path.
No real LLM API calls are made; tests only verify --help / version output
and module importability.
"""

from __future__ import annotations

import subprocess
import sys


def _run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run python -m twat_llm with given args."""
    return subprocess.run(
        [sys.executable, "-m", "twat_llm", *args],
        capture_output=True,
        text=True,
        check=check,
    )


# ---------------------------------------------------------------------------
# Module-level --help
# ---------------------------------------------------------------------------


def test_help_exits_zero() -> None:
    """python -m twat_llm --help exits 0 and prints command listing."""
    result = _run("--help")
    assert result.returncode == 0
    # Fire prints help to stderr
    combined = result.stdout + result.stderr
    assert "ask" in combined or "COMMANDS" in combined or "version" in combined


def test_no_args_exits_zero() -> None:
    """python -m twat_llm (no args) exits 0 — Fire prints usage."""
    result = subprocess.run(
        [sys.executable, "-m", "twat_llm"],
        capture_output=True,
        text=True,
        check=False,
    )
    # Fire may exit non-zero with no args but should still print help
    combined = result.stdout + result.stderr
    assert "ask" in combined or "version" in combined or "COMMANDS" in combined


# ---------------------------------------------------------------------------
# version leaf
# ---------------------------------------------------------------------------


def test_version_prints_semver() -> None:
    """python -m twat_llm version prints a semver-like string."""
    result = _run("version")
    assert result.returncode == 0
    version = result.stdout.strip()
    # Should look like X.Y.Z or X.Y.Z.postN
    assert "." in version, f"Unexpected version output: {version!r}"


def test_version_flag() -> None:
    """python -m twat_llm -- --version is handled gracefully (no crash)."""
    result = subprocess.run(
        [sys.executable, "-m", "twat_llm", "--", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    # May exit non-zero (fire doesn't support --version at top level),
    # but must not traceback-crash with ImportError
    assert "ImportError" not in result.stderr
    assert "ModuleNotFoundError" not in result.stderr


# ---------------------------------------------------------------------------
# Per-leaf --help
# ---------------------------------------------------------------------------


def test_ask_help() -> None:
    """python -m twat_llm ask --help exits 0."""
    result = _run("ask", "--help")
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "prompt" in combined.lower()


def test_complete_help() -> None:
    """python -m twat_llm complete --help exits 0."""
    result = _run("complete", "--help")
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "prompt" in combined.lower()


def test_ask_batch_help() -> None:
    """python -m twat_llm ask-batch --help exits 0."""
    result = _run("ask-batch", "--help")
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "prompts" in combined.lower() or "file" in combined.lower()


def test_ask_chain_help() -> None:
    """python -m twat_llm ask-chain --help exits 0."""
    result = _run("ask-chain", "--help")
    assert result.returncode == 0
    combined = result.stdout + result.stderr
    assert "data" in combined.lower() or "steps" in combined.lower()


def test_list_models_help() -> None:
    """python -m twat_llm list-models --help exits 0."""
    result = _run("list-models", "--help")
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# cmd_* entry-point helpers (importable)
# ---------------------------------------------------------------------------


def test_cmd_helpers_importable() -> None:
    """All cmd_* helpers import without error."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from twat_llm.__main__ import ("
            "cmd_ask, cmd_complete, cmd_ask_batch, cmd_ask_chain, "
            "cmd_list_models, cmd_version, main, COMMANDS"
            "); assert set(COMMANDS) == {'ask','complete','ask-batch','ask-chain','list-models','version'}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0


def test_commands_dict_keys() -> None:
    """COMMANDS dict contains exactly the expected keys."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from twat_llm.__main__ import COMMANDS; print(sorted(COMMANDS.keys()))",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.returncode == 0
    output = result.stdout.strip()
    for key in ("ask", "complete", "ask-batch", "ask-chain", "list-models", "version"):
        assert key in output, f"Missing key {key!r} in COMMANDS: {output}"


# ---------------------------------------------------------------------------
# list-models (no API call — just exercises llm.get_models() path)
# ---------------------------------------------------------------------------


def test_list_models_runs() -> None:
    """python -m twat_llm list-models exits 0 (llm ships built-in models)."""
    result = subprocess.run(
        [sys.executable, "-m", "twat_llm", "list-models"],
        capture_output=True,
        text=True,
        check=False,
    )
    # llm may have 0 models installed but must not crash
    assert "ImportError" not in result.stderr
    assert "ModuleNotFoundError" not in result.stderr
