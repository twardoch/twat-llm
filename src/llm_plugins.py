"""Check which LLM plugins are installed and display results in a table."""

from __future__ import annotations

import importlib
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from fire import Fire
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class PackageResult:
    """Result of checking a package installation."""

    name: str
    status: str
    duration: float
    details: str = ""


def check_package(package: str) -> PackageResult:
    """Check if a package can be imported.

    Args:
        package: Name of package to check

    Returns:
        PackageResult containing status and timing information
    """
    start_time = time.time()
    try:
        importlib.import_module(package)
        duration = time.time() - start_time
        return PackageResult(package, "SUCCESS", duration)
    except ImportError as e:
        duration = time.time() - start_time
        return PackageResult(package, "FAILED", duration, str(e))


def create_results_table(results: Sequence[PackageResult]) -> Table:
    """Create formatted table of package check results.

    Args:
        results: Sequence of package check results

    Returns:
        Rich Table object with formatted results
    """
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Package")
    table.add_column("Status", justify="center")
    table.add_column("Time (s)", justify="right")
    table.add_column("Details")

    for result in sorted(results, key=lambda x: x.duration, reverse=True):
        status_color = "green" if result.status == "SUCCESS" else "red"
        table.add_row(
            result.name,
            f"[{status_color}]{result.status}[/{status_color}]",
            f"{result.duration:.4f}",
            result.details,
        )
    return table


def check_llm_plugins(packages: Sequence[str] | None = None) -> None:
    """Check which LLM plugins are installed and display results in a table.

    Args:
        packages: Optional sequence of package names to check. If None, checks default LLM plugins.
    """
    if packages is None:
        packages = [
            "llm",
            "llm_claude_3",
            "llm_cmd",
            "llm_cmd_comp",
            "llm_consortium",
            "llm_fireworks",
            "llm_gemini",
            "llm_groq",
            "llm_groq_whisper",
            "llm_horde",
            "llm_huggingface",
            "llm_hyperbolic",
            "llm_inference",
            "llm_interpolate",
            "llm_jina_api",
            "llm_jq",
            "llm_judge",
            "llm_mistral",
            "llm_mlc",
            "llm_nomic_api_embed",
            "llm_openrouter",
            "llm_perplexity",
            "llm_python",
            "llm_reka",
            "llm_replicate",
            "llm_sambanova",
            "llm_structure",
            "llm_together",
            "llm_topology",
            "llm_utils",
            "llm_whisper_api",
        ]

    results = [check_package(pkg) for pkg in packages]
    table = create_results_table(results)
    console = Console()
    console.print(table)


if __name__ == "__main__":
    Fire(check_llm_plugins)
