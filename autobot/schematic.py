import difflib
import json
import os
from typing import NamedTuple

from colorama import Fore

from autobot.transforms import TransformType

BEFORE_FILENAME: str = "before.py"
AFTER_FILENAME: str = "after.py"


class SchematicDefinitionException(Exception):
    pass


class Schematic(NamedTuple):
    title: str
    before_text: str
    after_text: str
    before_description: str
    after_description: str
    transform_type: TransformType

    @classmethod
    def from_directory(cls, dirname: str) -> "Schematic":
        """Load a Schematic from a directory."""
        # Attempt to load the schematic.
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

        before_filename: str = os.path.join(dirname, BEFORE_FILENAME)
        if not os.path.isfile(before_filename):
            raise SchematicDefinitionException(
                f"Unable to find file: {before_filename}"
            )

        with open(before_filename, "r") as fp:
            before_text: str = fp.read()

        after_filename: str = os.path.join(dirname, AFTER_FILENAME)
        if not os.path.isfile(after_filename):
            raise SchematicDefinitionException(f"Unable to find file: {after_filename}")

        with open(after_filename, "r") as fp:
            after_text = fp.read()

        autobot: str = os.path.join(dirname, "autobot.json")
        if not os.path.isfile(autobot):
            raise SchematicDefinitionException(f"Unable to find file: {autobot}")

        with open(autobot, "r") as fp:
            metadata = json.load(fp)
            if not (before_description := metadata.get("before_description")):
                raise SchematicDefinitionException(
                    f"autobot.json is missing `before_description`"
                )
            if not (after_description := metadata.get("after_description")):
                raise SchematicDefinitionException(
                    f"autobot.json is missing `after_description`"
                )
            if not (transform_type_raw := metadata.get("transform_type")):
                raise SchematicDefinitionException(
                    f"autobot.json is missing `transform_type`"
                )

            try:
                transform_type: TransformType = TransformType(transform_type_raw)
            except ValueError:
                raise SchematicDefinitionException(
                    f"Invalid `transform_type`: '{transform_type_raw}'. Choose one of: "
                    f"{[member.value for member in TransformType]}."
                )

        return cls(
            title=title,
            before_text=before_text,
            after_text=after_text,
            before_description=before_description,
            after_description=after_description,
            transform_type=transform_type,
        )

    def print_diff(self) -> None:
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
