"""Entrypoint to the autobot CLI."""
from __future__ import annotations

import argparse
import logging
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler


def run(options: Any) -> None:
    from autobot import api
    from autobot.refactor import run_refactor
    from autobot.schematic import Schematic, SchematicDefinitionException
    from autobot.utils import filesystem

    api.init()

    model: str = options.model
    nthreads: int = options.nthreads
    verbose: bool = options.verbose

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M:%S",
        level=logging.INFO if verbose else logging.WARNING,
        handlers=[RichHandler()],
    )

    console = Console()

    try:
        schematic: Schematic = Schematic.from_directory(options.schematic)
    except SchematicDefinitionException as error:
        console.print(f"[bold red]error[/]  {error}")
        exit(1)

    targets = filesystem.collect_python_files(options.files)
    if not targets:
        console.print(f"[bold red]error[/]  No Python files found")
        exit(1)

    run_refactor(
        schematic=schematic,
        targets=targets,
        nthreads=nthreads,
        model=model,
    )


def review(options: Any) -> None:
    from autobot.review import run_review

    run_review()


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="autobot", description="An automated code refactoring tool."
    )
    subparsers = parser.add_subparsers()

    # autobot run
    parser_run = subparsers.add_parser(
        "run",
        description="An automated code refactoring tool.",
        usage="autobot run [schematic] [files [files ...]]",
    )
    parser_run.add_argument(
        "schematic", type=str, help="Path to the autobot schematic."
    )
    parser_run.add_argument(
        "files", type=str, nargs="+", help="Path to the files to refactor."
    )
    parser_run.add_argument(
        "--model",
        type=str,
        default="text-davinci-002",
        choices=(
            "text-davinci-002",
            "text-curie-001",
            "text-babbage-001",
            "text-ada-001",
            "code-davinci-002",
            "code-cushman-001",
        ),
        help=(
            "The OpenAI model to use when generating completions. "
            "(Note: OpenAI's Codex models are currently in private beta.)"
        ),
    )
    parser_run.add_argument(
        "--nthreads",
        type=int,
        default=8,
        help="The number of threads to use when generating completions.",
    )
    parser_run.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output.",
    )
    parser_run.set_defaults(func=run)

    # autobot review
    parser_review = subparsers.add_parser(
        "review",
        description="An automated code refactoring tool.",
        usage="autobot review",
    )
    parser_review.set_defaults(func=review)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        console = Console()
        console.print(
            "[bold white]Usage: autobot run \[schematic] \[files \[files ...]]"
        )
        console.print()
        console.print("[bold white]An automated code refactoring tool.")
