import difflib
import functools
import logging
import os.path
from multiprocessing.pool import ThreadPool
from typing import Dict, List, Set, Tuple

from colorama import Fore
from rich.console import Console
from rich.progress import Progress

from autobot import prompt
from autobot.refactor import patches
from autobot.snippet import Snippet, iter_snippets, recontextualize
from autobot.transforms import TransformType


def fix_text(
    text: str,
    *,
    transform_type: TransformType,
    before_text: str,
    after_text: str,
    before_description: str,
    after_description: str,
    model: str,
) -> Tuple[str, str]:
    """Generate a fix for a snippet.

    Returns: a tuple of (snippet, suggested fix), to play nicely with multiprocessing.
    """
    return text, prompt.resolve_prompt(
        prompt.make_prompt(
            text,
            transform_type=transform_type,
            before_text=before_text,
            after_text=after_text,
            before_description=before_description,
            after_description=after_description,
        ),
        model=model,
    )


def run_refactor(
    *,
    title: str,
    before_filename: str,
    after_filename: str,
    targets: List[str],
    before_description: str,
    after_description: str,
    transform_type: TransformType,
    nthreads: int,
    model: str,
) -> None:
    with open(before_filename, "r") as fp:
        before_text = fp.read()

    with open(after_filename, "r") as fp:
        after_text = fp.read()

    console = Console()

    console.print(f"[bold]Running [bold cyan]{title}[/] based on user-provided example")

    console.print("-" * len(f"Running {title} based on user-provided example"))
    for line in difflib.unified_diff(
        before_text.splitlines(),
        after_text.splitlines(),
        lineterm="",
        fromfile=os.path.join("a", title, "before.py"),
        tofile=os.path.join("b", title, "after.py"),
    ):
        # TODO(charlie): Why is this necessary? Without it, blank lines contain
        # a single space.
        if len(line.strip()) == 0:
            line = line.strip()

        if line.startswith("-"):
            print(f"{Fore.RED}{line}{Fore.RESET}")
        elif line.startswith("+"):
            print(f"{Fore.GREEN}{line}{Fore.RESET}")
        else:
            print(line)
    console.print("-" * len(f"Running {title} based on user-provided example"))
    console.print()

    # Deduplicate targets, such that if we need to apply the same fix to a bunch of
    # snippets, we only make a single API call.
    console.print("[bold]1. Extracting AST nodes...")
    filename_to_snippets: Dict[str, List[Snippet]] = {}
    all_snippet_texts: Set[str] = set()
    for filename in targets:
        with open(filename, "r") as fp:
            source_code = fp.read()

        filename_to_snippets[filename] = []
        for snippet in iter_snippets(source_code, transform_type.ast_node_type()):
            max_snippet_len = 1600
            if len(snippet.text) > max_snippet_len:
                logging.warning(
                    f"Snippet at {filename}:{snippet.lineno} is too long "
                    f"({len(snippet.text)} > {max_snippet_len}); skipping..."
                )
                continue
            filename_to_snippets[filename].append(snippet)
            all_snippet_texts.add(snippet.text)

    # Map from snippet text to suggested fix.
    console.print("[bold]2. Generating completions...")
    snippet_text_to_completion: Dict[str, str] = {}
    with Progress(transient=True, console=console) as progress:
        task = progress.add_task("", total=len(all_snippet_texts))
        with ThreadPool(processes=nthreads) as pool:
            for text, completion in pool.map(
                functools.partial(
                    fix_text,
                    transform_type=transform_type,
                    before_text=before_text,
                    after_text=after_text,
                    before_description=before_description,
                    after_description=after_description,
                    model=model,
                ),
                all_snippet_texts,
            ):
                progress.update(task, advance=1)
                snippet_text_to_completion[text] = completion

    # Format each suggestion as a patch.
    console.print("[bold]3. Constructing patches...")
    count: int = 0
    for target in filename_to_snippets:
        with open(target, "r") as fp:
            source = fp.read()

        for text, padding, lineno in filename_to_snippets[target]:
            before_text = text
            after_text = snippet_text_to_completion[text]
            patch: str = ""
            for line in difflib.unified_diff(
                recontextualize(Snippet(before_text, padding, lineno), source),
                recontextualize(Snippet(after_text, padding, lineno), source),
                lineterm="",
                fromfile=os.path.join("a", target),
                tofile=os.path.join("b", target),
            ):
                # TODO(charlie): Why is this necessary? Without it, blank lines contain
                # a single space.
                stripped = line.strip()
                if len(stripped) == 0:
                    line = stripped

                patch += line
                patch += "\n"

            # Save the patch.
            if patch:
                patches.save(patch, target=target, lineno=lineno)
                count += 1

    console.print()
    if count == 0:
        console.print(f"[bold white]✨ Done! No suggestions found.")
    elif count == 1:
        console.print(f"[bold white]✨ Done! Generated {count} patch.")
    else:
        console.print(f"[bold white]✨ Done! Generated {count} patches.")
