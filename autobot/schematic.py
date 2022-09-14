from __future__ import annotations

import ast
import difflib
import os
from typing import NamedTuple

from autobot.transforms import TransformType

BEFORE_FILENAME: str = "before.py"
AFTER_FILENAME: str = "after.py"


class SchematicDefinitionException(Exception):
    pass


def extract_transform_type(source_code: str) -> TransformType | None:
    for node in ast.walk(ast.parse(source_code)):
        for transform_type in TransformType:
            if isinstance(node, transform_type.ast_node_type()):
                return transform_type
    else:
        return None


def extract_source(source_code: str) -> str | None:
    for node in ast.walk(ast.parse(source_code)):
        for transform_type in TransformType:
            if isinstance(node, transform_type.ast_node_type()):
                return ast.get_source_segment(source_code, node)
    else:
        return None


def extract_description(source_code: str) -> str | None:
    for node in ast.walk(ast.parse(source_code)):
        if isinstance(node, ast.Module):
            return ast.get_docstring(node)
    else:
        return None


class Schematic(NamedTuple):
    title: str
    before_text: str
    after_text: str
    before_description: str
    after_description: str
    transform_type: TransformType

    @classmethod
    def from_directory(cls, dirname: str) -> Schematic:
        """Load a Schematic from a directory."""
        dirname = dirname.rstrip("/")
        title = os.path.basename(dirname)

        if not os.path.isdir(dirname):
            # Fallback: this could be a schematic that ships with autobot (i.e. a path
            # relative to ./schematics).
            bundled_dirname = os.path.join(
                os.path.dirname(__file__), "schematics", dirname
            )

            if not os.path.isdir(bundled_dirname):
                raise SchematicDefinitionException(f"Directory not found: {dirname}")

            dirname = bundled_dirname

        before_filename = os.path.join(dirname, BEFORE_FILENAME)
        if not os.path.isfile(before_filename):
            raise SchematicDefinitionException(
                f"Unable to find file: {before_filename}"
            )

        with open(before_filename, "r") as fp:
            source_code = fp.read()
            if not (transform_type := extract_transform_type(source_code)):
                raise SchematicDefinitionException(
                    f"Invalid transform type found in: {before_filename}"
                )
            if not (before_text := extract_source(source_code)):
                raise SchematicDefinitionException(
                    f"No source node found in: {before_filename}"
                )
            if not (before_description := extract_description(source_code)):
                raise SchematicDefinitionException(
                    f"No description found in: {before_filename}"
                )
            before_description = before_description.lstrip(".").rstrip(".")

        after_filename = os.path.join(dirname, AFTER_FILENAME)
        if not os.path.isfile(after_filename):
            raise SchematicDefinitionException(f"Unable to find file: {after_filename}")

        with open(after_filename, "r") as fp:
            source_code = fp.read()
            if not (after_text := extract_source(source_code)):
                raise SchematicDefinitionException(
                    f"No source node found in: {after_filename}"
                )
            if not (after_description := extract_description(source_code)):
                raise SchematicDefinitionException(
                    f"No description found in: {after_filename}"
                )
            after_description = after_description.lstrip(".").rstrip(".")

        return cls(
            title=title,
            before_text=before_text,
            after_text=after_text,
            before_description=before_description,
            after_description=after_description,
            transform_type=transform_type,
        )

    def print_diff(self) -> None:
        from colorama import Fore

        for line in difflib.unified_diff(
            self.before_text.splitlines(),
            self.after_text.splitlines(),
            lineterm="",
            fromfile=os.path.join("a", self.title, BEFORE_FILENAME),
            tofile=os.path.join("b", self.title, AFTER_FILENAME),
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
