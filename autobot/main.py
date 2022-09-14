"""Entrypoint to the autobot CLI."""
import argparse
import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from autobot.transforms import TransformType


def run(options: Any) -> None:
    from autobot import api
    from autobot.refactor import run_refactor
    from autobot.utils import filesystem

    api.init()

    nthreads: int = options.nthreads
    verbose: bool = options.verbose

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M:%S",
        level=logging.INFO if verbose else logging.WARNING,
        handlers=[RichHandler()],
    )

    console = Console()

    # Attempt to load the schematic.
    schematic: str = options.schematic.rstrip("/")
    if not os.path.isdir(schematic):
        # Fallback: this could be a schematic that ships with autobot (i.e. a path
        # relative to ./schematics).
        bundled_schematic = os.path.join(
            os.path.dirname(__file__), "schematics", schematic
        )

        if os.path.isdir(bundled_schematic):
            schematic = bundled_schematic
        else:
            console.print(f"[bold red]error[/]  Directory not found: {schematic}")
            exit(1)

    before_filename: str = os.path.join(schematic, "before.py")
    if not os.path.isfile(before_filename):
        console.print(f"[bold red]error[/]  Unable to find file: {before_filename}")
        exit(1)

    after_filename: str = os.path.join(schematic, "after.py")
    if not os.path.isfile(after_filename):
        console.print(f"[bold red]error[/]  Unable to find file: {after_filename}")
        exit(1)

    autobot: str = os.path.join(schematic, "autobot.json")
    if not os.path.isfile(autobot):
        console.print(f"[bold red]error[/]  Unable to find file: {autobot}")
        exit(1)

    with open(autobot, "r") as fp:
        metadata = json.load(fp)
        if not (before_description := metadata.get("before_description")):
            console.print(
                f"[bold red]error[/]  autobot.json is missing `before_description`"
            )
            exit(1)
        if not (after_description := metadata.get("after_description")):
            console.print(
                f"[bold red]error[/]  autobot.json is missing `after_description`"
            )
            exit(1)
        if not (transform_type_raw := metadata.get("transform_type")):
            console.print(
                f"[bold red]error[/]  autobot.json is missing `transform_type`"
            )
            exit(1)

        try:
            transform_type: TransformType = TransformType(transform_type_raw)
        except ValueError:
            console.print(
                "[bold red]error[/]  "
                f"Invalid `transform_type`: '{transform_type_raw}'. Choose one of: "
                f"{[member.value for member in TransformType]}."
            )
            exit(1)

    targets = filesystem.collect_python_files(options.files)
    if not targets:
        console.print(f"[bold red]error[/]  No Python files found")
        exit(1)

    run_refactor(
        title=os.path.basename(schematic),
        before_filename=before_filename,
        after_filename=after_filename,
        targets=targets,
        before_description=before_description,
        after_description=after_description,
        transform_type=transform_type,
        nthreads=nthreads,
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
