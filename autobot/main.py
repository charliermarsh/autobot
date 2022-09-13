"""Entrypoint to the autobot CLI."""
import argparse
import json
import logging
import os
from typing import Any, List

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

from autobot.transforms import TransformType


def run(options: Any) -> None:
    from autobot import api
    from autobot.refactor import run_refactor

    api.init()

    schematic: str = options.schematic
    nthreads: int = options.nthreads
    verbose: bool = options.verbose

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M:%S",
        level=logging.DEBUG if verbose else logging.INFO,
        handlers=[RichHandler()],
    )

    console = Console()

    # Attempt to load the schematic.
    if not os.path.isdir(schematic):
        # Fallback: this could be a schematic that ships with autobot (i.e. a path
        # relative to ./schematics).
        schematic = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "schematics", schematic
        )

        if not os.path.isdir(schematic):
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

    targets: List[str] = options.target

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

    parser = argparse.ArgumentParser(prog="autobot")
    subparsers = parser.add_subparsers()

    # autobot run
    parser_run = subparsers.add_parser("run")
    parser_run.add_argument(
        "schematic", type=str, help="Path to the autobot schematic."
    )
    parser_run.add_argument(
        "target", type=str, nargs="+", help="Path to the files to refactor."
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
        help="Whether to print our completions.",
    )
    parser_run.set_defaults(func=run)

    # autobot review
    parser_review = subparsers.add_parser("review")
    parser_review.set_defaults(func=review)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_usage()
